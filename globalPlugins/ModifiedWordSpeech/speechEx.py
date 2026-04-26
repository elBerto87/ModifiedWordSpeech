# globalPlugins\ModifiedWordSpeech\speechEx.py

import re
import speech.speech
import api
import config
import textInfos
from controlTypes.state import State


def speakTypedCharacters(obj, ch: str):
	if api.isTypingProtected():
		return

	# Trigger on separators, punctuation, and enter
	if not ch.isalnum() or ch == "\b":
		speakPreviousWord(obj, ch)


def speakPreviousWord(obj, ch):
	if not config.conf.get("keyboard", {}).get("speakTypedWords"):
		return

	# Optimized READONLY check
	if State.READONLY in obj.states:
		return

	word = ""

	try:
		# Safe TextInfo retrieval
		try:
			info = obj.makeTextInfo(textInfos.POSITION_CARET)
		except Exception:
			# Fallback for broken caret (e.g. LibreOffice Writer on Enter)
			review = api.getReviewPosition()
			if not review:
				return
			info = review.copy()

		line_info = info.copy()
		is_enter = ch in ("\r", "\n")

		if is_enter:
			# Attempt 1: previous line (Chromium / Notepad++)
			line_info.move(textInfos.UNIT_LINE, -1)
			line_info.expand(textInfos.UNIT_LINE)
			text_content = line_info.text

			# Attempt 2 (Writer): fallback to previous word if line is empty
			if not text_content or not text_content.strip():
				line_info = info.copy()
				line_info.move(textInfos.UNIT_CHARACTER, -1)
				line_info.expand(textInfos.UNIT_WORD)
				text_content = line_info.text
		else:
			# Space / punctuation handling
			line_info.expand(textInfos.UNIT_LINE)
			line_info.setEndPoint(info, "endToEnd")
			text_content = line_info.text

		if not text_content:
			return

		# Basic cleanup
		clean_text = (
			text_content.replace("\xa0", " ")
			.replace("\r", "")
			.replace("\n", "")
		)

		# --- Anti-duplication logic ---
		if not is_enter and ch != "\b":
			text_before = (
				text_content[:-len(ch)]
				if text_content.endswith(ch)
				else text_content
			)
			if text_before and not text_before[-1].isalnum():
				return

		elif is_enter:
			if clean_text and not clean_text[-1].isalnum():
				return
		# -----------------------------

		# Word extraction
		if not is_enter and ch != "\b" and clean_text.endswith(ch):
			text_to_search = clean_text[:-len(ch)].rstrip()
		else:
			text_to_search = clean_text.rstrip()

		match = re.search(r"(\w+)$", text_to_search)
		if match:
			word = match.group(1)

	except Exception:
		pass

	# Clear buffer and speak
	speech.speech.clearTypedWordBuffer()

	if word and word.strip():
		if word != ch:
			speech.speech.speakText(word)