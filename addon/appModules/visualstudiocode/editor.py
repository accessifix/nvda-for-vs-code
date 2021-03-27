# Author: Pawel Urbanski <support@accessifix.com> under GPL licence.
# Contains shared code imported by release specific modules.
# NVDA Add-on for Microsoft Visual studio Code

import re
import api
import appModuleHandler
import braille
import controlTypes as cTs
from controlTypes import OutputReason 
import eventHandler
import IAccessibleHandler
from eventHandler import isPendingEvents
import keyboardHandler
import oleacc
import speech
from speech.priorities import Spri
import textInfos
import ui
from logHandler import log
from NVDAObjects import NVDAObject
from NVDAObjects.IAccessible import IAccessible
from NVDAObjects.IAccessible import chromium as Electron
from NVDAObjects.IAccessible import ia2Web
from NVDAObjects.IAccessible.ia2TextMozilla import MozillaCompoundTextInfo

# from NVDAObjects.IAccessible.ia2Web import Editor as BaseEditor
from NVDAObjects.behaviors import EditableText, EditableTextWithAutoSelectDetection
from scriptHandler import script


class VSCodeEditor(EditableTextWithAutoSelectDetection):

	# Set editor role to an empty string to prevent reading on every focus.
	roleText = str("\0")
	roleTextBraille = str("\0")

	# Remove states that are not needed to be announced on every focus.
	# We overwrite a default method for a control that returns states.
	def _get_states(self):
		states = super(VSCodeEditor, self).states
		states.discard(cTs.STATE_AUTOCOMPLETE)
		states.discard(cTs.STATE_MULTILINE)
		return states

	# Normalize and compare 2 strings.
	def isSameEditor(self, currentName: str):
		cN = str(currentName).lower()
		lN = str(self.appModule.lastEditorName).lower()
		if cN == lN:
			self.appModule.lastEditorName = cN
			return True
		else:
			self.appModule.lastEditorName = cN
			# The focus shifted to a new document and we are in a different line.
			return False

	# Handle gain focus event for the editor.
	def event_gainFocus(self):
		if self.isSameEditor(self.name):
			self.name = None
			speech.cancelSpeech()
		else:
			nameToSpeak = []
			nameToSpeak.append(str(self.name))
			speech.speak(nameToSpeak)
			self.name = None

		super(VSCodeEditor, self).event_gainFocus()
		speech.cancelSpeech()
		self.processLine()

	def processLine(self):
		# Cancel speech in advance.

		# Get the textInfo object for a current line
		currentLine = self.makeTextInfo(textInfos.POSITION_SELECTION)
		currentLine.collapse()
		currentLine.expand(textInfos.UNIT_LINE)
		# Assign short variables for later conditions
		lastStartOffset = self.appModule.lastStartOffset
		currentStartOffset = currentLine._start._startOffset

		# We want to prevent speaking the line from its beginning
		# after every code completion.
		# We may use the offsets for more advanced cases in the future.
		# @todo: Prevent previously typed characters
		# at the beginning of the line.
		if lastStartOffset == currentStartOffset:
			currentCursor = self.makeTextInfo(textInfos.POSITION_SELECTION)
			currentCursor._start._startOffset = currentCursor._start._endOffset
			currentCursor.collapse()
			currentCursor.expand(textInfos.UNIT_CHARACTER)
			speech.cancelSpeech()

			speech.speakTextInfo(
				currentCursor,
				textInfos.UNIT_CHARACTER,
				reason=OutputReason.FOCUS,
				suppressBlanks=True,
			)
			self.appModule.lastStartOffset = currentStartOffset
		else:
			otherLine = self.makeTextInfo(textInfos.POSITION_SELECTION)
			otherLine.collapse()
			otherLine.expand(textInfos.UNIT_LINE)
			speech.speakTextInfo(
				otherLine,
				textInfos.UNIT_LINE,
				reason=OutputReason.FOCUS,
			)
			self.appModule.lastStartOffset = otherLine._start._startOffset

	# Handle lost focus event for the editor
	def event_loseFocus(self):
		# Set the name of the editor to none to prevent speaking when focus is lost.
		# The name of a currently opened file can be read from the window title.
		self.name = None
		super(VSCodeEditor, self).event_loseFocus()

	def event_caret(self):
		super(VSCodeEditor, self).event_caret()
		if self is api.getFocusObject() and not eventHandler.isPendingEvents('gainFocus'):
			self.detectPossibleSelectionChange()
		tx = self.makeTextInfo(textInfos.POSITION_SELECTION)
		tx.collapse()
		tx.expand(textInfos.UNIT_LINE)
		lineStart = tx._start._startOffset
		if not self.appModule.lastStartOffset == lineStart:
			self.appModule.lastStartOffset = lineStart
