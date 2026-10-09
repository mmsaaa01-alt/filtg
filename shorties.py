# shorties.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Map subjects to your folder names (must match your actual folder names exactly)
SUBJECT_FOLDERS = {
    "Mathematics": "mat",
    "History": "his",
    "Geography": "geo",
    "Economics": "eco",
    "Civics": "cit"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

async def shorties_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📘 Grade 9 Shorties", callback_data="shorties_grade_9")],
        [InlineKeyboardButton("📙 Grade 10 Shorties", callback_data="shorties_grade_10")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🤫 **Secret Vault: Shorties**\n\n"
        "Quick revision notes. Select your grade to access the vault:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def shorties_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # 1. Grade 9 Selection -> Show Subjects
    if data == "shorties_grade_9":
        keyboard = []
        for subject in SUBJECT_FOLDERS.keys():
            keyboard.append([InlineKeyboardButton(f"📚 {subject}", callback_data=f"shorties_subj_{subject.lower()}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="shorties_back")])
        await query.edit_message_text("📚 **Select a Subject for Grade 9:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    # 2. Grade 10 Selection -> Coming Soon
    elif data == "shorties_grade_10":
        await query.edit_message_text(
            "🚧 **Grade 10 Shorties are coming soon!** 🚧\n\n"
            "We are currently compiling the best notes for Grade 10. Stay tuned!", 
            parse_mode="Markdown"
        )
        return

    # 3. Subject Selection -> Show Units (files in folder)
    elif data.startswith("shorties_subj_"):
        subject_key = data.split("_")[2]
        subject_name = next((k for k, v in SUBJECT_FOLDERS.items() if k.lower() == subject_key), None)
        folder_name = SUBJECT_FOLDERS.get(subject_name)

        if not folder_name:
            await query.edit_message_text("⚠️ Subject folder mapping missing.")
            return

        folder_path = os.path.join(BASE_DIR, folder_name)
        
        # Explicit error if folder doesn't exist so you know exactly what to fix
        if not os.path.exists(folder_path):
            await query.edit_message_text(
                f"⚠️ The folder `{folder_name}` is missing in your bot directory!\n\n"
                f"Please create a folder named `{folder_name}` and add `.txt` files inside it.",
                parse_mode="Markdown"
            )
            return

        # Dynamically find all .txt files
        files = sorted([f for f in os.listdir(folder_path) if f.endswith('.txt')])
        if not files:
            await query.edit_message_text(
                f"📂 The `{folder_name}` folder is empty!\n\n"
                f"Please add `.txt` files (like `u1.txt`) inside it.",
                parse_mode="Markdown"
            )
            return

        keyboard = []
        for f in files:
            unit_name = f.replace('.txt', '').upper()
            keyboard.append([InlineKeyboardButton(f"📄 {unit_name}", callback_data=f"shorties_file_{subject_key}_{f}")])

        keyboard.append([InlineKeyboardButton("⬅️ Back to Subjects", callback_data="shorties_back_to_subj")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"📂 **{subject_name} Notes**\nSelect a unit to read:", reply_markup=reply_markup, parse_mode="Markdown")

    # 4. Unit Selection -> Read and Display the Note
    elif data.startswith("shorties_file_"):
        parts = data.split("_")
        subject_key = parts[2]
        filename = parts[3]
        subject_name = next((k for k, v in SUBJECT_FOLDERS.items() if k.lower() == subject_key), None)
        folder_name = SUBJECT_FOLDERS.get(subject_name)
        file_path = os.path.join(BASE_DIR, folder_name, filename)

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            unit_display = filename.replace('.txt', '').upper()
            
            # Telegram text limit is 4096. If short, show as text. If long, send as file.
            if len(content) <= 4000:
                await query.edit_message_text(
                    f"📄 **{subject_name} - {unit_display}**\n\n`{content}`", 
                    parse_mode="Markdown"
                )
            else:
                await query.answer("Note is long, sending as file...", show_alert=False)
                with open(file_path, 'rb') as file:
                    await context.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=file,
                        caption=f"📄 **{subject_name} - {unit_display}**",
                        parse_mode="Markdown"
                    )
        else:
            await query.edit_message_text("⚠️ File not found.")

    # 5. Back buttons
    elif data == "shorties_back":
        keyboard = [
            [InlineKeyboardButton("📘 Grade 9 Shorties", callback_data="shorties_grade_9")],
            [InlineKeyboardButton("📙 Grade 10 Shorties", callback_data="shorties_grade_10")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🤫 **Secret Vault: Shorties**\n\nSelect your grade:", reply_markup=reply_markup, parse_mode="Markdown")

    elif data == "shorties_back_to_subj":
        keyboard = []
        for subject in SUBJECT_FOLDERS.keys():
            keyboard.append([InlineKeyboardButton(f"📚 {subject}", callback_data=f"shorties_subj_{subject.lower()}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="shorties_back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📚 **Select a Subject for Grade 9:**", reply_markup=reply_markup, parse_mode="Markdown")