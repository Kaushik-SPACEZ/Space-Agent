import os
import re
import tempfile
import webbrowser
import html as _html
from email.message import EmailMessage
import streamlit as st
from dotenv import load_dotenv
 
# Load environment variables (AICORE_* etc.)
load_dotenv()
 
st.set_page_config(page_title="AI Email Generator — Auto Generate on Enter", layout="wide")
 
# GenAI Hub SDK - OpenAI compatible proxy
from gen_ai_hub.proxy.native.openai import chat
 
# From your uploaded image history
FILE_URL = "/mnt/data/620bae2e-a5a1-49ce-a0b8-c89eadaf199d.png"
 
# ------------------------------
# Styling  (WHITE UI)
# ------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #ffffff; color: #111827; }
    .subject-badge { padding:6px 10px; background:#2563eb; color:#ffffff; border-radius:8px; font-weight:600; display:inline-block; }
    .small-muted { color:#6b7280; font-size:13px; }
    .emoji-icon { font-size:2.3rem; margin-right:0.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ------------------------------
# Constants
# ------------------------------
TEMPLATE_PROMPTS = {
    "None": "",
    "Formal Request": "Write a formal business request email.",
    "Leave Request": "Write a professional leave request email to a manager.",
    "Follow-up Email": "Write a polite follow-up email asking for an update.",
    "Reminder Email": "Write a polite reminder email.",
    "Apology Email": "Write a sincere apology email.",
}
SIDEBAR_TONES = ["Friendly", "Professional", "Concise", "Urgent", "Apology"]
TONE_INSTRUCTIONS = {
    "Friendly": "Use a warm, friendly, conversational tone.",
    "Professional": "Use a formal and businesslike tone.",
    "Concise": "Be brief and direct.",
    "Urgent": "Convey urgency and need for fast action.",
    "Apology": "Use a sincere and apologetic tone.",
}
LANG_OPTIONS = ["English", "Hindi", "German", "French"]
LANG_INSTRUCTIONS = {
    "English": "Write the email in English.",
    "Hindi": "Write the email in Hindi.",
    "German": "Write the email in German.",
    "French": "Write the email in French.",
}
 
# ------------------------------
# State init
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_email" not in st.session_state:
    st.session_state.last_email = None
if "last_subject" not in st.session_state:
    st.session_state.last_subject = "AI Generated Email"
if "sidebar_tone" not in st.session_state:
    st.session_state.sidebar_tone = "Friendly"
if "sidebar_lang" not in st.session_state:
    st.session_state.sidebar_lang = "English"
if "hindi_transliterate" not in st.session_state:
    st.session_state.hindi_transliterate = False
if "model_name" not in st.session_state:
    st.session_state.model_name = "gpt-4o-mini"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.25
 
# We'll store the last user prompt and the settings used to create that prompt
if "last_user_prompt" not in st.session_state:
    st.session_state.last_user_prompt = None
if "last_settings" not in st.session_state:
    st.session_state.last_settings = None
 
# ------------------------------
# Helper: Extract subject
# ------------------------------
def extract_subject_and_body(text: str):
    if not text:
        return None, ""
    m = re.match(r"^\s*Subject\s*:\s*(.+?)(\r?\n)", text, flags=re.I)
    if m:
        return m.group(1).strip(), text[m.end():].lstrip()
    return None, text
 
# ------------------------------
# GenAI Hub call
# ------------------------------
def call_genai_chat(messages, model="gpt-4o-mini", temperature=0.25) -> str:
    response = chat.completions.create(
        model_name=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content
 
# ------------------------------
# FIX: Build PROPER HTML .eml for Outlook
# ------------------------------
def make_eml_bytes(subject: str, body: str) -> bytes:
    """Create fully HTML-preserved email for Outlook draft."""
    looks_like_html = bool(re.search(r"<\w+.*?>", body))
    if looks_like_html:
        html_body = body
        if not body.strip().lower().startswith("<html"):
            html_body = f"<html><body>{body}</body></html>"
    else:
        escaped = _html.escape(body)
        normalized = escaped.replace("\r\n", "\n")
        paragraphs = normalized.split("\n\n")
        html_paras = []
        for p in paragraphs:
            p_html = p.replace("\n", "<br/>")
            html_paras.append(
                f"<p style='margin:0 0 10px 0;'>{p_html}</p>"
            )
        html_body = (
            "<html><body style='font-family:Arial; font-size:14px; color:#111;'>" + "".join(html_paras) + "</body></html>"
        )
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["To"] = ""
    msg["From"] = ""
    msg["X-Unsent"] = "1"
    msg.set_content("This is an HTML email. Please view in HTML mode.")
    msg.add_alternative(html_body, subtype="html")
    return msg.as_bytes()
 
# ------------------------------
# Sidebar Controls
# ------------------------------
st.sidebar.header("✉️ Email Options")
template = st.sidebar.selectbox("Template style", list(TEMPLATE_PROMPTS.keys()))
tone = st.sidebar.selectbox("Tone", SIDEBAR_TONES)
lang = st.sidebar.selectbox("Language", LANG_OPTIONS)
 
# keep session_state mirrors updated for easier access elsewhere
st.session_state.sidebar_tone = tone
st.session_state.sidebar_lang = lang
if lang == "Hindi":
    st.session_state.hindi_transliterate = st.sidebar.checkbox(
        "Transliterate Hindi → English letters",
        value=st.session_state.hindi_transliterate,
    )
else:
    st.session_state.hindi_transliterate = False
 
with st.sidebar.expander("Model settings"):
    st.session_state.model_name = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0,
    )
    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 1.0, 0.25, 0.05
    )
 
# Helper to capture a tuple of the current settings
def current_settings_tuple():
    return (
        template,
        tone,
        lang,
        st.session_state.model_name,
        float(st.session_state.temperature),
        bool(st.session_state.hindi_transliterate),
    )
 
# ------------------------------
# Header
# ------------------------------
st.markdown(
    """
    <div style="display:flex; align-items:center; gap:0.6rem;">
      <div class="emoji-icon">📧</div>
      <h1>AI Email Generator</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("Type your prompt and press Enter. Email generates automatically.")
 
# ------------------------------
# Chat input (auto generate)
# ------------------------------
user_input = st.chat_input("Example: Write an email for 2-day leave.")
 
# If the user typed a fresh prompt, store it
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.last_user_prompt = user_input
    st.session_state.last_settings = current_settings_tuple()
 
# Show the user message in the live chat UI
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
 
# Decide whether settings have changed since last generation
settings_changed = False
if st.session_state.last_user_prompt and st.session_state.last_settings:
    if current_settings_tuple() != st.session_state.last_settings:
        settings_changed = True
 
# If we have a stored user prompt and settings changed, allow regenerate
regenerate_button_clicked = False
if st.session_state.last_user_prompt and settings_changed:
    if st.button("🔄 Regenerate with updated settings"):
        regenerate_button_clicked = True
 
# If a new prompt was entered or the regenerate button clicked, call the model
if user_input or regenerate_button_clicked:
    sys_prompt = "You are an expert assistant that writes clear professional emails."
    if template != "None":
        sys_prompt += " " + TEMPLATE_PROMPTS[template]
    sys_prompt += " " + TONE_INSTRUCTIONS[tone]
    sys_prompt += " " + LANG_INSTRUCTIONS[lang]
    if lang == "Hindi" and st.session_state.hindi_transliterate:
        sys_prompt += " Use Latin script for all Hindi words."

    # 🔹 NEW: force fresh subject + strict format
    sys_prompt += """
When generating the email, ALWAYS include a correct and new Subject line derived ONLY from the user's request.
Never reuse any previous subject from the conversation.

Format your output EXACTLY like this:

Subject: <new subject based on the user's current prompt>

<email body>

Do NOT wrap the output in markdown.
Do NOT include extra labels.
Return only the subject line followed by the email body.
"""

    prompt_to_use = st.session_state.last_user_prompt if st.session_state.last_user_prompt else user_input
    combined = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt_to_use}]
 
    with st.spinner("Generating email..."):
        ai_response = call_genai_chat(
            combined,
            model=st.session_state.model_name,
            temperature=st.session_state.temperature,
        )
 
    subj, body = extract_subject_and_body(ai_response)
    st.session_state.last_subject = subj or st.session_state.last_subject
    st.session_state.last_email = body
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    st.session_state.last_settings = current_settings_tuple()
 
# ------------------------------
# Show Email  (Subject visible in UI)
# ------------------------------
if st.session_state.last_email:
    st.subheader("Generated Email")

    # editable subject field
    st.session_state.last_subject = st.text_input(
        "Subject",
        value=st.session_state.last_subject,
        key="subject_input",
    )

    shown_tone = st.session_state.sidebar_tone
    shown_lang = st.session_state.sidebar_lang
    st.markdown(
        f"""
        <div style="padding:14px; background:rgba(255,255,255,0.8); border-radius:10px;">
          <span class="subject-badge">📩 {st.session_state.last_subject}</span>
          <div class="small-muted">Tone: {shown_tone} • Language: {shown_lang}</div>
          <hr/>
          <div style="white-space:pre-wrap;">{st.session_state.last_email}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
 
# ------------------------------
# Outlook Draft Button (with formatting)
# ------------------------------
if st.session_state.last_email:
    if st.button("📨 Open in Outlook (Draft)"):
        try:
            eml_bytes = make_eml_bytes(st.session_state.last_subject, st.session_state.last_email)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as f:
                f.write(eml_bytes)
                fpath = f.name
            webbrowser.open(fpath)
            st.success("Draft opened in Outlook with perfect formatting ✔")
        except Exception as e:
            st.error("Error opening Outlook draft: " + str(e))
 
# ------------------------------
# Post-generation quick actions
# Shorten / Expand / Improve subject
# ------------------------------
def _call_rewrite_action(action_label: str, instruction: str):
    """Helper to call the model to rewrite the latest email according to `instruction`."""
    if not st.session_state.last_email:
        st.warning("No generated email to modify.")
        return
    sys_prompt = "You are an expert assistant that writes clear professional emails."
    if template != "None":
        sys_prompt += " " + TEMPLATE_PROMPTS[template]
    sys_prompt += " " + TONE_INSTRUCTIONS[tone]
    sys_prompt += " " + LANG_INSTRUCTIONS[lang]

    # 🔹 Also enforce the same output structure for rewrites
    sys_prompt += """
When rewriting the email, keep the same intent and include a proper Subject line.
Format your output EXACTLY like this:

Subject: <subject>

<email body>

Do NOT wrap the output in markdown.
Do NOT include extra labels.
Return only the subject line followed by the email body.
"""
 
    user_content = (
        f"Instruction: {instruction}\n\nOriginal Email:\n{st.session_state.last_email}\n\n"
        "Please return only the rewritten email. If you change the subject, start with a 'Subject: ...' line."
    )
 
    with st.spinner(f"{action_label}..."):
        rewritten = call_genai_chat(
            [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_content}],
            model=st.session_state.model_name,
            temperature=st.session_state.temperature,
        )
 
    subj, body = extract_subject_and_body(rewritten)
    st.session_state.last_subject = subj or st.session_state.last_subject
    st.session_state.last_email = body or rewritten
    st.success(f"{action_label} applied")
 
# Show quick-action buttons when email is present
if st.session_state.last_email:
    st.markdown("\n---\n")
    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        if st.button("🧩 Shorten"):
            _call_rewrite_action(
                "Shorten",
                "Shorten this email while preserving the main meaning and polite tone.",
            )

    with col2:
        if st.button("🧱 Expand"):
            _call_rewrite_action(
                "Expand",
                "Expand this email with a bit more detail and clarity while keeping the same intent.",
            )

    with col3:
        if st.button("📌 Improve subject"):
            _call_rewrite_action(
                "Improve subject",
                "Improve only the subject line of this email to be clear and professional. "
                "Keep the body mostly the same. Respond with 'Subject: ...' and the email body.",
            )
 
    st.markdown("\n---\n")
 
# ------------------------------
# Extra: hint about regenerate availability
# ------------------------------
if st.session_state.last_user_prompt and settings_changed:
    st.info("You changed settings since the last generation. Click '🔄 Regenerate with updated settings' to re-generate using the saved prompt.")
 
# End of file
