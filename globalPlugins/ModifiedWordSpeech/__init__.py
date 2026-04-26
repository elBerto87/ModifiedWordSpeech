# globalPlugins\ModifiedWordSpeech\__init__.py
# -*- coding: UTF-8 -*-
"""
ModifiedWordSpeech NVDA Add-on

This add-on is an independent adaptation inspired by functionality originally
present in the NVDAExtensionGlobalPlugin add-on by Paulber19.

Original concept and implementation:
- NVDAExtensionGlobalPlugin by Paulber19 and contributors
- https://github.com/paulber19/NVDAExtensionGlobalPlugin

That functionality was removed in version 13.3 of the original project,
but has been reimplemented here as a lightweight standalone add-on.

This implementation has been rewritten and adapted for modern NVDA versions
and maintained as an independent project.

Copyright (c) 2026 Alessio Bertucci

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

This project is provided "as is", without warranty of any kind.
"""
import addonHandler
addonHandler.initTranslation()

try:
	_  # type: ignore
except NameError:
	_ = lambda s: s  # Fallback if translations are not available

import globalPluginHandler
import config
import editableText
import globalVars
import winUser
from tones import beep
from logHandler import log
from controlTypes import *
from .speechEx import speakTypedCharacters

_target_classes = {
	"Edit",
	"RichEdit",
	"Scintilla",
	"Chrome_RenderWidgetHostHWND",
	"RenderWidgetHostHWND",
	"SALFRAME",
}

_target_roles = {ROLE_DOCUMENT, ROLE_EDITABLETEXT, ROLE_TERMINAL}


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if globalVars.appArgs.secure or obj.appModule.appName.startswith("musescore"):
			return

		# Safe extraction of window class (avoids crashes in secure contexts)
		window_class = getattr(obj, "windowClassName", "")

		if (
			obj.role in _target_roles
			or window_class in _target_classes
			or any(editableText.EditableText in cls.__mro__ for cls in clsList)
		):
			if EditableTextUseTextInfoToSpeakTypedWords not in clsList:
				clsList.insert(0, EditableTextUseTextInfoToSpeakTypedWords)


class EditableTextUseTextInfoToSpeakTypedWords(editableText.EditableText):
	def event_typedCharacter(self, ch: str):
		try:
			speakTypedCharacters(self, ch)
		except Exception:
			pass

		try:
			kb_conf = config.conf.get("keyboard", {})

			if (
				kb_conf.get("beepForLowercaseWithCapslock")
				and ch.islower()
				and winUser.getKeyState(winUser.VK_CAPITAL) & 1
			):
				beep(3000, 40)

			if not ch.isalnum() and ch != "\b":
				doc_conf = config.conf.get("documentFormatting", {})
				if doc_conf.get("reportSpellingErrors") and kb_conf.get(
					"alertForSpellingErrors"
				):
					self._reportErrorInPreviousWord()
		except Exception:
			pass

		super().event_typedCharacter(ch)