# Author: Pawel Urbanski <support@accessifix.com> under GPL licence.
# Contains shared code imported by release specific modules.
# NVDA Add-on for Microsoft Visual studio Code

import api
import appModuleHandler
import braille
import controlTypes as cTs
import eventHandler
import IAccessibleHandler
import keyboardHandler
import oleacc
import speech
import textInfos
import ui
from comtypes import COMError
from logHandler import log
from NVDAObjects.IAccessible import IAccessible
from NVDAObjects.IAccessible import chromium as Electron
from NVDAObjects.IAccessible import ia2Web
from NVDAObjects.IAccessible.ia2TextMozilla import MozillaCompoundTextInfo
from NVDAObjects.IAccessible.ia2Web import Editor as BaseEditor
from scriptHandler import script


class CodeEditor(BaseEditor):

	# Remove states that are not needed to be announced on every focus.
	# We overwrite a default method for a control that returns states.
	def _get_states(self):
		states = super(CodeEditor, self).states
		states.discard(cTs.STATE_AUTOCOMPLETE)
		states.discard(cTs.STATE_MULTILINE)
		return states

	# Handle gain focus event for the editor.
	def event_gainFocus(self):
		# Set the name of the editor to none to preventing speakint on every focus.
		# The name of a currently opened file can be larnt from the widnow title.
		# Set the role to an empty string instead of 'edit'.
		# It will be skipped and not announced on every focus.
		# This change applies only to the main code editor.
		self.name = None
		self.roleText = str('\0')
		super(CodeEditor,self).event_gainFocus()
		self.processLine()

	# Handle lost focus event for the editor
	def event_loseFocus(self):
		# Set the name of the editor to none to preventing speakint on every focus.
		# The name of a currently opened file can be larnt from the widnow title.
		self.name = None
		super(CodeEditor,self).event_loseFocus()

	# Logic for processing lines of code
	def processLine(self):
		# Get the textInfo object for a current line
		currentLine = self.makeTextInfo(textInfos.POSITION_SELECTION)
		currentLine.collapse()
		currentLine.expand(textInfos.UNIT_LINE)
		# Assign short variables for later conditions
		lastOffset = self.appModule.lastStartOffset
		currentOffset = currentLine._start._startOffset
		# We want to prevent speaking the line from its beginning
		# after every code completion.
		# We may use the offsets for more advanced cases in the future.
		if lastOffset == currentOffset:
			self.appModule.lastStartOffset = currentOffset
			# Do not read the line, but it gets displayed in Braille.
			speech.cancelSpeech()
		else:
			self.appModule.lastStartOffset = currentOffset
			# Read the line - selection gets marked in Braille.
			speech.cancelSpeech()
			speech.speakTextInfo(currentLine, textInfos.UNIT_LINE, reason=cTs.REASON_FOCUS)
			return


class AppModule(appModuleHandler.AppModule):

	# This module-scoped variable holds last start offset.
	# It is declared on a module scope to not be reset within a editor class.
	lastStartOffset = 0 # It is 0 in an empty file.

	# Initialization method called on add-on load.
	def __init__(self, *args, **kwargs):
	# It will prevent speaking the type on every focus.
		super(AppModule, self).__init__(*args, **kwargs)
		cTs.silentRolesOnFocus.add(cTs.ROLE_TREEVIEW)
		cTs.silentRolesOnFocus.add(cTs.ROLE_TREEVIEWITEM)

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(AppModule, self).chooseNVDAObjectOverlayClasses(obj, clsList)
	# Overwrite the standard editor class with a custom for Visual Studio Code.
		if obj.windowClassName == "Chrome_RenderWidgetHostHWND" and obj.role == cTs.ROLE_EDITABLETEXT and cTs.STATE_MULTILINE in obj.states:
			clsList.insert(0, CodeEditor)

	# Send escape key to the application
	# we must capture escape to prevent losing focus
	def script_FixFocus(self, gesture):
		gesture.send()
	__gestures = {
		"kb:escape":"FixFocus",
	}

	# Add back TREVIEW and TREEVIEWITEM to roles spoken on focus.
	def terminate(self):
		cTs.silentRolesOnFocus.discard(cTs.ROLE_TREEVIEW)
		cTs.silentRolesOnFocus.discard(cTs.ROLE_TREEVIEWITEM)
