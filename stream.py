# streamlit_app.py

# Import the Streamlit library, commonly aliased as 'st'.
import streamlit as st
# Import the 'os' module for operating system dependent functionality, like path manipulation.
import os
# Import specific classes from the Pillow library (PIL fork) for image handling.
from PIL import Image, ImageDraw, UnidentifiedImageError
# Import the 'io' module, specifically 'BytesIO' for handling binary data (like image bytes) in memory.
import io

# Import necessary functions and data structures defined in the local 'ut.py' file.
from ut import (
    load_calorie_table, get_unit_options, convert_to_grams,
    get_calories_per_gram, predict_food_label_roboflow,
    calculate_total_calories_new, chatbot_response, # Ensure chatbot_response is imported
    QUALITATIVE_UNIT_TERMS, CORE_UNITS # Import lists needed for logic
)

# --- Define Roboflow Classes explicitly (Optional but good for reference) ---
ROBOFLOW_KNOWN_CLASSES = [
    "apple_pie", "baby_back_ribs", "baklava", "beet_salad", "breakfast_burrito",
    "caesar_salad", "cannoli", "carrot_cake", "cheese_plate", "cheesecake",
    "chicken_curry", "chicken_quesadilla", "chicken_wings", "chocolate_cake",
    "chocolate_mousse", "churros", "club_sandwich", "cup_cakes", "donuts",
    "falafel", "fish_and_chips", "french_fries", "french_toast", "fried_rice",
    "frozen_yogurt", "garlic_bread", "greek_salad", "grilled_salmon", "hamburger",
    "hot_dog", "hummus", "ice_cream", "lasagna", "nachos", "omelette", "pizza",
    "samosa", "steak", "tacos", "waffles",
]

# --- PRED_TO_TITLE: Specific Overrides ---
PRED_TO_TITLE = {
    "french_fries": "French Fries",
    "baby_back_ribs": "Baby Back Ribs",
}


# --- Page Configuration ---
st.set_page_config(page_title="CAMHEALTH - AI Calorie Estimator", layout="centered", page_icon="🥗")

# --- App Title Area ---
# Use the title from the second script which mentions chat
st.title("🍽️ Welcome to CAMHEALTH")
st.markdown("Estimate calories from your food photos using AI chat.")
st.divider()

# --- Load Data & API Key ---
@st.cache_data # Cache the loaded data
def get_calorie_data(file_path="calorie_table_processed.csv"):
    """Loads the processed calorie data using ut.load_calorie_table."""
    data = load_calorie_table(file_path)
    if data is None:
        st.error(f"❌ Critical Error: Could not load or process calorie data from '{file_path}'. Check console logs for details.")
        st.stop()

    # label_map: List of tuples (lowercase_label_from_csv, Display_Label_from_csv)
    label_map = sorted(
        [(key, details[0]) for key, details in data.items()],
        key=lambda item: item[1] # Sort by Display_Label_from_csv
    )
    # all_food_display_labels: Includes "--- Select ---" + all display labels from CSV
    all_labels = ["--- Select ---"] + [item[1] for item in label_map]
    return data, label_map, all_labels

# Load base data from CSV using the ut function
calorie_data, food_label_map, all_food_display_labels = get_calorie_data()


# --- Load API Key ---
try:
    # Use hardcoded keys for demo, replace with st.secrets in production
    ROBOFLOW_API_KEY = "THhSSer2p8KwaihhPrWF" # st.secrets["ROBOFLOW_API_KEY"]
    ROBOFLOW_MODEL_ID = "food-101-ih2pp/4"    # st.secrets["ROBOFLOW_MODEL_ID"]
    ROBOFLOW_API_URL = "https://detect.roboflow.com" # For serverless classification

    if not ROBOFLOW_API_KEY or not isinstance(ROBOFLOW_API_KEY, str):
         raise ValueError("ROBOFLOW_API_KEY not found or is not a string.")
    if not ROBOFLOW_MODEL_ID or not isinstance(ROBOFLOW_MODEL_ID, str):
         raise ValueError("ROBOFLOW_MODEL_ID not found or is not a string.")
    if not ROBOFLOW_API_URL or not isinstance(ROBOFLOW_API_URL, str):
         raise ValueError("ROBOFLOW_API_URL not found or is not a string.")

except (KeyError, ValueError) as e:
    st.error(f"🚨 Error loading Roboflow Configuration: {e}")
    st.stop()
except Exception as e:
    st.error(f"🚨 An unexpected error occurred reading configuration: {e}")
    st.stop()


# --- Session State Initialization ---
# Use the initialization adapted from the second script to include chat state
if "app_reset_trigger" not in st.session_state:
     st.session_state.app_reset_trigger = 0

def initialize_state():
    st.session_state.step = 0
    st.session_state.image_bytes = None
    st.session_state.image_caption = ""
    st.session_state.meal_items = {} # Use {label_lower: total_grams} structure
    st.session_state.current_main_label = "" # Stores the lower_label of the main item
    st.session_state.predicted_label = None
    st.session_state.predicted_confidence = None
    st.session_state.error_message = ""
    st.session_state.info_message = ""
    st.session_state.widget_key_base = 1000
    st.session_state.predicted_display_label = None
    st.session_state.total_calories = 0
    st.session_state.item_details = {}

    # Add state vars used in snippet logic specifically for clearing messages on change
    keys_to_clear = ['last_selected_confirm', 'last_selected_unit_main',
                     'last_selected_extra', 'last_selected_extra_unit',
                     'calories_calculated'] # Add calories_calculated flag
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    else:
        st.session_state.chat_messages = [] # Clear on reset

    # Thread ID
    st.session_state.thread_id = None


if "step" not in st.session_state or st.session_state.app_reset_trigger > 0:
     initialize_state()
     st.session_state.app_reset_trigger = 0 # Reset trigger after initialization


# --- Helper Functions ---
def reset_app_state():
    """Resets the application state by triggering re-initialization."""
    st.session_state.app_reset_trigger += 1

def get_lower_label_from_display(display_label):
     """Finds the internal lowercase label corresponding to a display label FROM THE CSV data map."""
     if not display_label or display_label == "--- Select ---":
         return None
     # Check explicit map first
     for lower, display in food_label_map:
         if display == display_label:
             return lower
     # Fallback checks (copied from second script's helper)
     display_label_lower = display_label.lower()
     if display_label_lower in calorie_data:
         return display_label_lower
     simple_lower = display_label.lower().replace(" ", "_").strip()
     if simple_lower in calorie_data:
         return simple_lower
     print(f"Warning (get_lower_label_from_display): Could not map display label '{display_label}' to a known lower label key.")
     return None # Return None if not found

def format_display_label(lower_label):
     """Converts any lowercase label (predicted or from CSV) to a display-friendly format."""
     if not lower_label:
         return None
     # 1. Check specific overrides first
     if lower_label in PRED_TO_TITLE:
         return PRED_TO_TITLE[lower_label]
     # 2. Check if the label exists in the calorie_data to get the original capitalization
     if calorie_data and lower_label in calorie_data:
         return calorie_data[lower_label][0] # Use the Original_Label from the CSV data tuple
     else:
         # Fallback to simple formatting if not in CSV (likely a prediction)
         return lower_label.replace("_", " ").title()

# --- Display Image ---
def display_image(image_bytes, caption):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, caption=caption, use_container_width=True)
    except UnidentifiedImageError:
        st.error("❌ Could not display image. Invalid format.")
    except Exception as e:
        st.error(f"An error occurred displaying the image: {e}")

# --- Chat UI Helpers (adapted from second script) ---
def display_chat_history():
    """Displays the chat messages stored in session state."""
    # Removed expander for now, keep it simple
    if not st.session_state.chat_messages:
        st.caption("Chat history will appear here.") # More descriptive placeholder
    else:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def add_chat_message(role, content):
    """Adds a message to the chat history."""
    st.session_state.chat_messages.append({"role": role, "content": content})


# ================================================
# == STEP 0: Initial State & Upload ==
# ================================================
if st.session_state.step == 0:
    st.info("👋 Welcome! Upload a photo of your meal to begin.")
    uploaded_file = st.file_uploader(
        "Upload Meal Photo",
        type=["jpg", "jpeg", "png"],
        key=f"uploader_{st.session_state.widget_key_base}",
        label_visibility="collapsed"
    )
    if uploaded_file:
        # Initialize state (includes clearing chat)
        initialize_state()
        st.session_state.image_bytes = uploaded_file.getvalue()
        st.session_state.image_caption = uploaded_file.name
        st.session_state.step = 1 # Move to predicting step
        st.rerun()


# ================================================
# == STEP 1: Predicting & Initial Chat ==
# ================================================
if st.session_state.step == 1:
    if st.session_state.image_bytes:
        display_image(
            st.session_state.image_bytes,
            f"Analyzing: {st.session_state.image_caption}" # Show caption during analysis
        )
        with st.spinner("🤖 Analyzing image with CAMHEALTH AI..."):
            try:
                pred_label_raw, pred_confidence = predict_food_label_roboflow(
                    image_bytes=st.session_state.image_bytes,
                    api_key=ROBOFLOW_API_KEY,
                    model_id=ROBOFLOW_MODEL_ID,
                    api_url=ROBOFLOW_API_URL # Pass the API URL
                )
                print("confidence", pred_confidence)
                if pred_confidence < 0.7: 
                    st.session_state.error_message = "⚠️ CAMHEALTH could not identify the food. Please select manually below."
                    add_chat_message("assistant", st.session_state.error_message) # Add this info to chat
                else:
                    st.session_state.predicted_label = pred_label_raw.lower().strip() if pred_label_raw else None
                    st.session_state.predicted_confidence = pred_confidence
                    st.session_state.predicted_display_label = format_display_label(st.session_state.predicted_label)

                    # --- Initial Chatbot message (from second script) ---
                    if st.session_state.predicted_label:
                        prompt = f"The AI analyzed the image and suggests the main food item is: **{st.session_state.predicted_display_label}**."
                        # Call chatbot_response with interaction code 1
                        response, thread_id = chatbot_response(prompt, 0, 1) # Start with None thread_id or 0
                        st.session_state.thread_id = thread_id # STORE thread_id
                        add_chat_message("assistant", response) # Store message
                    else:
                        # If prediction fails, inform user via chat
                        st.session_state.error_message = "⚠️ CAMHEALTH could not identify the food. Please select manually below."
                        add_chat_message("assistant", st.session_state.error_message) # Add this info to chat
                # --- End Initial Chatbot message ---

                st.session_state.step = 1.2 # Move to confirmation regardless of chat success/failure

            except Exception as e:
                 st.error(f"An error occurred during prediction: {e}")
                 st.session_state.error_message = f"Prediction failed: {e}"
                 # Add error message to chat
                 add_chat_message("assistant", f"Sorry, there was an error during image analysis: {e}")
                 # Allow user to proceed to manual selection even if prediction fails
                 st.session_state.step = 1.2

            st.rerun() # Rerun to show chat message and move to next step
    else:
        st.warning("No image found. Please upload again.")
        reset_app_state() # Use reset function
        st.rerun()


# ================================================
# == STEP 1.2: Confirm Prediction ==
# ================================================
if st.session_state.step == 1.2:
    # --- Display image + Back button ---
    if st.session_state.image_bytes:
        display_image(
            st.session_state.image_bytes,
            st.session_state.image_caption
        )
        st.markdown("---")
        if st.button("⬅️ Change Photo", key="back_to_upload"):
             reset_app_state() # Use reset function
             st.rerun()
    else:
        st.warning("Image data missing. Please start over.")
        reset_app_state() # Use reset function
        st.rerun()

    # --- Display Chat History (includes the first chatbot message) ---
    display_chat_history()
    st.markdown("---")
    # --- End Chat Display ---

    # --- Combined Confirmation / Modification UI (from first script) ---
    pred_lower = st.session_state.predicted_label
    display_label_suggestion = st.session_state.predicted_display_label

    dropdown_options = list(all_food_display_labels)
    is_suggestion_new = False
    if display_label_suggestion and display_label_suggestion not in dropdown_options:
        dropdown_options.insert(1, display_label_suggestion)
        is_suggestion_new = True

    default_idx = 0
    if display_label_suggestion and display_label_suggestion in dropdown_options:
        try: default_idx = dropdown_options.index(display_label_suggestion)
        except ValueError: default_idx = 0

    # Subheader message - Reuse from first script (more informative than just chat)
    if display_label_suggestion:
        subheader_msg = f"🤖 CAMHEALTH suggests: **{st.session_state.predicted_display_label}**" # Use state var directly
        if st.session_state.predicted_confidence is not None:
             subheader_msg += f""
    else:
        subheader_msg = "⚠️ CAMHEALTH could not identify the food. Please select manually."
    st.subheader(subheader_msg) # Show suggestion clearly outside chat

    # --- Selectbox and Confirm Button (Logic from first script) ---
    # Using st.form from second script for better grouping is fine
    with st.form(key="confirm_food_form"):
        st.markdown("👇 Please select or confirm the main food item.") # Adjusted prompt slightly
        selected_display_label = st.selectbox(
            "Confirm or select item:", # Label inside form
            options=dropdown_options, # Use combined list
            index=default_idx,
            key=f"confirm_selectbox_{st.session_state.widget_key_base}",
            label_visibility="collapsed" # Hide redundant label
        )

        # Clear previous errors when selection changes (inside form is okay)
        if 'last_selected_confirm' not in st.session_state or st.session_state.last_selected_confirm != selected_display_label:
            st.session_state.error_message = ""
            st.session_state.info_message = ""
            st.session_state.last_selected_confirm = selected_display_label

        submitted = st.form_submit_button("✅ Confirm Selection & Specify Quantity") # Button text implies next step

        if submitted:
            if selected_display_label and selected_display_label != "--- Select ---":
                # Determine the confirmed lower label (handling AI suggestion case)
                confirmed_lower_label = None
                if is_suggestion_new and selected_display_label == display_label_suggestion:
                    confirmed_lower_label = pred_lower
                else:
                    confirmed_lower_label = get_lower_label_from_display(selected_display_label)
                    if confirmed_lower_label is None and selected_display_label == display_label_suggestion:
                         confirmed_lower_label = pred_lower # Handle existing suggestion selection

                if confirmed_lower_label:
                     # Final check: Does the confirmed item have calorie data?
                     cal_check = get_calories_per_gram(confirmed_lower_label, calorie_data)
                     if cal_check is None:
                          # Allow proceeding but warn (using st.warning inside form is fine)
                          st.warning(f"⚠️ Calorie data not found for '{selected_display_label}' in CSV. Calorie estimation may be 0.")
                          # No need for info_message here if warning shown

                     # Proceed to quantify step
                     st.session_state.current_main_label = confirmed_lower_label # Store lowercase label
                     st.session_state.step = 1.5 # Move to quantify step
                     st.session_state.error_message = "" # Clear errors before moving
                     st.session_state.info_message = ""
                     st.session_state.widget_key_base += 1
                     # Optional: Add user confirmation to chat log
                     # add_chat_message("user", f"Confirmed item: {selected_display_label}")
                     st.rerun()
                else:
                     # Error within the form
                     st.error(f"❌ Internal error: Could not map '{selected_display_label}' back to data key.")
            else:
                # Warning within the form
                st.warning("⚠️ Please select a food item first.")


# ================================================
# == STEP 1.5: Quantify Main Dish ==
# ================================================
if st.session_state.step == 1.5:
    # Check if main item label exists
    if not st.session_state.current_main_label:
        st.warning("No main item selected. Please go back.")
        if st.button("⬅️ Back to Select"):
            st.session_state.step = 1.2 # Go back to confirmation
            st.rerun()
        st.stop()

    main_label_lower = st.session_state.current_main_label
    main_display_label = format_display_label(main_label_lower) # Use consistent helper

    # --- Variant Feature (from first script) ---
    FOOD_VARIANT_MAP = {
        "pizza": [
            "Pizza Slice Cheese", "Pizza Slice Pepperoni", "Pizza Slice Margherita",
            "Pizza Slice Veggie", "Pizza Slice Meat Lovers", "Pizza Slice Hawaiian",
            "Pizza Slice Supreme", "Pizza Slice BBQ Chicken", "Pizza Slice White",
            "Personal Pizza Cheese",
        ],
        "hamburger": [
            "Burger Plain", "Cheeseburger", "Bacon Cheeseburger", "Veggie Burger",
            "Black Bean Burger Patty" ,"Lebanese Burger",
        ],
        "pasta": [ # Added example
            "Pasta Plain Cooked", "Pasta Bolognese Dish", "Pasta Carbonara Dish",
            "Pasta Pesto Dish", "Pasta Alfredo Dish", "Pasta Marinara Dish",
        ],
    }
    variant_options = FOOD_VARIANT_MAP.get(main_label_lower.split(" ")[0], []) # Basic check on first word for variants

    if variant_options:
        st.markdown("### Select Specific Variant (if applicable)")
        selected_variant = st.selectbox(
            f"Choose variant for {main_display_label}",
            options=["--- Select ---"] + variant_options,
            key=f"variant_selectbox_{st.session_state.widget_key_base}"
        )

        if selected_variant != "--- Select ---":
            variant_lower_check = get_lower_label_from_display(selected_variant)
            if variant_lower_check:
                main_label_lower = variant_lower_check
                main_display_label = selected_variant
            else:
                st.warning(f"Could not map variant '{selected_variant}' to data. Using original item.")
    # --- End Variant Feature ---

    # --- Back button ---
    if st.button("⬅️ Back to Select Item", key="back_to_confirm_from_quantify"):
        st.session_state.current_main_label = ""
        st.session_state.step = 1.2
        st.rerun()

    st.subheader(f"2. Enter Quantity of '{main_display_label}'")
    st.markdown("Select a portion size or enter quantity and unit.")

    available_units = get_unit_options(main_label_lower)

    # Use Form for Quantity Input (good idea from second script)
    with st.form(key="quantity_form"):
        col_amt, col_unit = st.columns([1, 2])

        with col_unit:
            unit_index = 0
            unit = st.selectbox("Unit", options=available_units if available_units else ["N/A"],
                                key=f"unit_selector_main_{st.session_state.widget_key_base}",
                                index=unit_index, label_visibility="collapsed",
                                disabled=not available_units)

        unit_lower = unit.lower() if unit and unit != "N/A" else ""
        numeric_units = CORE_UNITS if 'CORE_UNITS' in globals() else ["grams", "oz", "ml", "fl oz", "cup", "tbsp", "tsp"]
        needs_numeric_amount = bool(unit_lower) and (unit_lower not in QUALITATIVE_UNIT_TERMS or unit_lower in numeric_units)

        with col_amt:
            amount_disabled = not needs_numeric_amount or not available_units
            amount_placeholder = "Amount" if needs_numeric_amount else "N/A (Standard)"
            amount_value = 1.0
            amount = st.number_input("Amount", min_value=0.1, step=0.1, value=amount_value,
                                     key=f"amount_input_main_{st.session_state.widget_key_base}",
                                     placeholder=amount_placeholder,
                                     label_visibility="collapsed",
                                     disabled=amount_disabled,
                                     format="%.1f" if needs_numeric_amount else None)
            if amount_disabled:
                amount = 1.0

        # Clear errors on unit change (logic from first script)
        if 'last_selected_unit_main' not in st.session_state or st.session_state.last_selected_unit_main != unit:
            st.session_state.error_message = "" # Clear external error message state too
            st.session_state.info_message = ""
            st.session_state.last_selected_unit_main = unit

        # Button text matches first script's workflow
        submitted_quantity = st.form_submit_button("➡️ Add Main Item & Continue")

        if submitted_quantity:
            if unit and unit != "N/A":
                # Validation
                if needs_numeric_amount and (amount is None or amount <= 0):
                    st.warning("⚠️ Please enter a positive amount for the selected unit.") # Warning inside form
                else:
                    amount_to_convert = amount if needs_numeric_amount else 1.0
                    grams_added = convert_to_grams(main_label_lower, amount_to_convert, unit, calorie_data)

                    if grams_added is not None and grams_added >= 0:
                        # Store grams (resetting meal_items)
                        st.session_state.meal_items = {main_label_lower: grams_added}
                        # Update current_main_label to reflect final choice
                        st.session_state.current_main_label = main_label_lower

                        # --- NO CHATBOT CALL HERE - PROCEED TO STEP 2 ---
                        st.session_state.step = 2 # Move to Add Extras
                        st.session_state.error_message = ""
                        # Set info message for success feedback outside form later
                        amount_str = f"{amount:.1f} " if needs_numeric_amount else ""
                        st.session_state.info_message = f"✅ Added {amount_str}{unit} of {main_display_label} (≈ {grams_added:.1f}g)."
                        st.session_state.widget_key_base += 1
                        if 'calories_calculated' in st.session_state: del st.session_state.calories_calculated
                        st.rerun()

                    elif grams_added is None:
                        st.error(f"⚠️ Could not convert '{unit}' for '{main_display_label}'. Check data or unit selection.") # Error inside form
                    else: # Negative grams
                        st.error("⚠️ Calculation resulted in negative grams. Check inputs.") # Error inside form
            else:
                 st.warning("⚠️ Please select a unit for the item.") # Warning inside form

    # Display success message from adding main item (outside form)
    if st.session_state.info_message:
        st.success(st.session_state.info_message)
        st.session_state.info_message = "" # Clear after displaying


# ================================================
# == STEP 2: Add Extras / Other Items ==
# ================================================
if st.session_state.step == 2:
    # --- Back button ---
    if st.button("⬅️ Back to Quantify Main", key="back_to_quantify_main"):
         st.session_state.step = 1.5
         st.rerun()

    st.subheader("3. Add Extras / Other Items (Optional)")
    st.markdown("Add sauces, toppings, sides, drinks, etc.")
    st.markdown("---")

    # --- Display Current Meal (from first script) ---
    with st.expander("View Current Meal Items", expanded=True):
        if not st.session_state.meal_items:
            st.caption("No items added yet.")
        else:
            items_copy = list(st.session_state.meal_items.items())
            main_item_label_lower = st.session_state.current_main_label

            for label_lower, total_grams in items_copy:
                is_main = label_lower == main_item_label_lower
                display_label = format_display_label(label_lower)
                item_text = f"• {display_label}" + (" (Main)" if is_main else "")

                col_text, col_button = st.columns([0.8, 0.2])
                with col_text:
                    st.write(f"{item_text}: ~{total_grams:.1f}g")
                with col_button:
                    remove_disabled = is_main
                    if st.button("❌", key=f"remove_{label_lower}_{st.session_state.widget_key_base}", help=f"Remove {display_label}", disabled=remove_disabled, use_container_width=True):
                        if not remove_disabled:
                            if label_lower in st.session_state.meal_items:
                                del st.session_state.meal_items[label_lower]
                            st.session_state.info_message = f"Removed {display_label}."
                            st.session_state.error_message = ""
                            st.rerun()
        st.markdown("---")

    # --- Add Extra Item (from first script) ---
    st.markdown("##### Add Another Item / Extra:")
    col1, col2, col3, col4 = st.columns([3, 1, 2, 1])

    with col1:
        extra_options = all_food_display_labels[1:]
        selected_extra_display = st.selectbox(
            "Select item", options=["--- Select ---"] + extra_options,
            key=f"extra_selector_{st.session_state.widget_key_base}", index=0,
            label_visibility="collapsed"
        )
        selected_extra_lower = get_lower_label_from_display(selected_extra_display) if selected_extra_display != "--- Select ---" else None

    available_units = get_unit_options(selected_extra_lower) if selected_extra_lower else []

    with col3: # Unit selection
        unit_index = 0
        unit = st.selectbox("Unit", options=available_units if available_units else ["N/A"],
                            key=f"unit_selector_extra_{st.session_state.widget_key_base}", index=unit_index,
                            label_visibility="collapsed",
                            disabled=not selected_extra_lower or not available_units)

    unit_lower = unit.lower() if unit and unit != "N/A" else ""
    numeric_units = CORE_UNITS if 'CORE_UNITS' in globals() else ["grams", "oz", "ml", "fl oz", "cup", "tbsp", "tsp"]
    needs_numeric_amount = bool(unit_lower) and (unit_lower not in QUALITATIVE_UNIT_TERMS or unit_lower in numeric_units)

    with col2: # Amount input
        amount_disabled = not selected_extra_lower or not needs_numeric_amount or not available_units or unit == "N/A"
        amount_placeholder = "Amount" if needs_numeric_amount else "N/A (Standard)"
        amount_value = 1.0
        amount = st.number_input("Amount", min_value=0.1, step=0.1, value=amount_value,
                                 key=f"amount_input_extra_{st.session_state.widget_key_base}",
                                 placeholder=amount_placeholder,
                                 label_visibility="collapsed",
                                 disabled=amount_disabled,
                                 format="%.1f" if needs_numeric_amount else None)
        if amount_disabled:
            amount = 1.0

    # Clear messages if selection changes (using first script state vars)
    if 'last_selected_extra' not in st.session_state or st.session_state.last_selected_extra != selected_extra_display:
         st.session_state.error_message = ""
         st.session_state.info_message = ""
         st.session_state.last_selected_extra = selected_extra_display
    if 'last_selected_extra_unit' not in st.session_state or st.session_state.last_selected_extra_unit != unit:
         st.session_state.error_message = ""
         st.session_state.info_message = ""
         st.session_state.last_selected_extra_unit = unit

    with col4: # Add button
        add_button_disabled = not selected_extra_lower or not unit or unit == "N/A"
        if st.button("➕ Add Item", key=f"add_extra_item_button_{st.session_state.widget_key_base}", disabled=add_button_disabled, use_container_width=True):
            if selected_extra_lower and unit and unit != "N/A":
                cal_check = get_calories_per_gram(selected_extra_lower, calorie_data)
                proceed_with_conversion = False
                warning_message = ""

                if cal_check is None:
                    warning_message = f"Note: Calorie data not found for '{selected_extra_display}'. Calorie estimation may be 0."
                    proceed_with_conversion = True # Allow adding

                if needs_numeric_amount and (amount is None or amount <= 0):
                    st.session_state.error_message = "⚠️ Please enter a positive amount for this unit."
                    proceed_with_conversion = False
                elif not proceed_with_conversion: # Check if not already blocked
                    proceed_with_conversion = True

                if proceed_with_conversion:
                    amount_to_convert = amount if needs_numeric_amount else 1.0
                    grams_added = convert_to_grams(selected_extra_lower, amount_to_convert, unit, calorie_data)

                    if grams_added is not None and grams_added >= 0:
                         st.session_state.meal_items[selected_extra_lower] = \
                             st.session_state.meal_items.get(selected_extra_lower, 0) + grams_added
                         amount_str = f"{amount:.1f} " if needs_numeric_amount else ""
                         current_total_g = st.session_state.meal_items[selected_extra_lower]
                         st.session_state.info_message = f"✅ Added/Updated {amount_str}{unit} of {selected_extra_display} (≈ {current_total_g:.1f}g total)."
                         if warning_message:
                             st.session_state.info_message += f" {warning_message}" # Append warning

                         st.session_state.error_message = ""
                         st.session_state.widget_key_base += 1
                         st.rerun()
                    elif grams_added is None:
                         st.session_state.error_message = f"⚠️ Could not convert '{unit}' for '{selected_extra_display}'. Check logs or data."
                    else: # Negative grams
                         st.session_state.error_message = "⚠️ Calculation resulted in negative grams."
            else:
                 st.session_state.error_message = "⚠️ Please select an item and unit."
            st.rerun() # Rerun to show messages


    # Display messages outside the columns
    if st.session_state.error_message:
        st.warning(st.session_state.error_message)
        st.session_state.error_message = "" # Clear after showing
    if st.session_state.info_message:
        st.info(st.session_state.info_message) # Use info for combined success/warning
        st.session_state.info_message = "" # Clear after showing

    # --- Finish Button & Chatbot Summary Trigger ---
    st.markdown("---")
    calculate_disabled = not st.session_state.meal_items
    if st.button("✅ Finish & Calculate Calories", key="calculate_button", use_container_width=True,
                 disabled=calculate_disabled):
        if not calculate_disabled:
            # --- Trigger final Chatbot Summary (Moved here from second script's Step 1.5/3) ---
            try:
                with st.spinner("📊 Finalizing calorie estimation..."):
                    # Calculate first
                    item_cal_details, total_meal_calories = calculate_total_calories_new(
                        st.session_state.meal_items, calorie_data
                    )
                    # Store results BEFORE calling chatbot
                    st.session_state.total_calories = total_meal_calories
                    st.session_state.item_details = item_cal_details

                    # Prepare prompt (similar to step 3 in second script)
                    meal_summary_list = []
                    missing_cal_data_note = False
                    for label, grams in st.session_state.meal_items.items(): # Iterate through final meal items
                        display_name = format_display_label(label)
                        # Get details from the *calculated* item_details
                        cals, status = st.session_state.item_details.get(label, (0.0, "error_missing_from_calc"))
                        cal_str = f"{cals:.0f} kcal"
                        if status != "calculated_per_gram":
                            cal_str += "*" # Indicate potential issue
                            if status == "error_missing_cals_per_gram": missing_cal_data_note = True
                        meal_summary_list.append(f"{display_name} (~{grams:.1f}g): {cal_str}")

                    meal_summary_str = "; ".join(meal_summary_list)
                    # Use the stored total_meal_calories
                    calorie_prompt = f"The total estimated calories for the meal ({meal_summary_str}) are **{st.session_state.total_calories:.0f} kcal**."
                    if missing_cal_data_note:
                        calorie_prompt += "\n(*Note: Calorie data was missing or incomplete for calculation; the total might be underestimated)."

                    # Get final summary response from chatbot - Use Interaction Code 3
                    response, thread_id = chatbot_response(calorie_prompt, st.session_state.thread_id, 3)
                    st.session_state.thread_id = thread_id # STORE thread_id
                    add_chat_message("assistant", response) # Store final summary message
                    st.session_state.calories_calculated = True # Set flag: calculation and summary done

            except Exception as e:
                st.error(f"Error during final calculation or chatbot interaction: {e}")
                # Still proceed to step 3 to show calculation results if they exist
                st.session_state.calories_calculated = True # Mark as calculated even if chat failed

            # --- End Chatbot Summary Trigger ---

            # Move to Results step
            st.session_state.step = 3
            st.session_state.error_message = ""
            st.session_state.info_message = ""
            st.rerun()
        # No else needed, button is disabled


# ================================================
# == STEP 3: Show Results & Open Chat ==
# ================================================
if st.session_state.step == 3:
     # Title from second script for chat context
     st.subheader("💬 CAMHEALTH Meal Summary & Chat")

     if not st.session_state.meal_items:
         st.warning("No meal items were added. Please go back and add items.")
         if st.button("⬅️ Go Back"):
             st.session_state.step = 2 # Go back to Add Extras
             # Clear potentially inconsistent state
             if 'calories_calculated' in st.session_state: del st.session_state.calories_calculated
             st.session_state.total_calories = 0
             st.session_state.item_details = {}
             st.rerun()
         st.stop()

     # --- Display Chat History (includes initial suggestion AND final summary) ---
     display_chat_history()
     st.markdown("---")
     # --- End Chat Display ---

     # Retrieve pre-calculated results (done at end of Step 2)
     total_meal_calories = st.session_state.total_calories
     item_cal_details = st.session_state.item_details

     st.markdown("**Final Meal Composition & Estimates:**")

     # Prepare data for display (using logic from first script)
     results_data = []
     missing_cal_data_note_display = False
     cal_data_issue_note_display = False
     for label_lower, total_grams in st.session_state.meal_items.items():
         display_name = format_display_label(label_lower)
         item_cals, status = item_cal_details.get(label_lower, (0.0, "error_missing_in_results"))
         cal_display = f"{item_cals:.0f} kcal"

         status_note = ""
         if status == "error_missing_cals_per_gram":
             status_note = "(Missing data)"
             missing_cal_data_note_display = True
         elif status != "calculated_per_gram":
             status_note = f"({status.replace('_', ' ')})"
             cal_data_issue_note_display = True

         results_data.append({
             "Item": display_name,
             "Total Grams (est.)": f"{total_grams:.1f}g",
             "Calories (est.)": cal_display,
             "Notes": status_note
         })

     st.dataframe(results_data, use_container_width=True, hide_index=True)
     st.markdown("---")
     # Display total metric
     st.metric(label="Total Estimated Meal Calories", value=f"{total_meal_calories:.0f} kcal")

     # Display notes based on calculation status
     if missing_cal_data_note_display:
         st.caption("Note: Items marked '(Missing data)' lacked specific calorie/gram info; their contribution is estimated as 0.")
     if cal_data_issue_note_display and not missing_cal_data_note_display:
         st.caption("Note: Some item calorie estimations may be less accurate due to data conversion issues.")

     # --- Open Chat Input (from second script) ---
     st.markdown("---")
     st.info("The floor is now open! Ask CAMHEALTH any questions about this meal.")
     user_query = st.chat_input("Ask about your meal...")
     if user_query:
         add_chat_message("user", user_query)
         # Call chatbot function with the user's query - Use Interaction Code 4
         with st.spinner("CAMHEALTH is thinking..."):
             response, thread_id = chatbot_response(user_query, st.session_state.thread_id, 4)
             st.session_state.thread_id = thread_id # Store potentially updated thread_id
             add_chat_message("assistant", response)
             st.rerun() # Rerun to display the new messages
     # --- End Open Chat Input ---

     st.markdown("---") # Divider before footer reset


# ================================================
# --- Footer / Reset (Shown on all steps > 0) ---
# ================================================
st.divider()
if st.session_state.step > 0:
    # Use the reset button text from the second script
    if st.button("🔁 Start New Meal Analysis", key="reset_button_footer"):
        reset_app_state() # Clears state including chat
        st.rerun()

# --- Footer / Disclaimer ---
st.caption("Powered by CAMHEALTH") # Use consistent branding
st.caption("Disclaimer: Calorie estimates are approximate and depend on accurate identification, portion estimation, and data completeness. Consult a nutritionist for precise dietary advice.")
