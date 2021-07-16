# Author: Pawel Urbanski <support@accessifix.com> under GPL licence.
# Contains shared code imported by release specific modules.
# NVDA Add-on for Microsoft Visual studio Code

from os import name
import api
import appModuleHandler
import braille
import controlTypes as cTs
import eventHandler
import IAccessibleHandler
import keyboardHandler
import oleacc
import speech
<<<<<<< HEAD
from speech import OutputReason
=======
from controlTypes import OutputReason
>>>>>>> 21.0
import textInfos
import ui
from comtypes import COMError
from logHandler import log
from NVDAObjects import NVDAObject
from NVDAObjects.IAccessible import IAccessible
from NVDAObjects.IAccessible.chromium import Document
from NVDAObjects.IAccessible import chromium as Electron
from NVDAObjects.IAccessible import ia2Web
from NVDAObjects.IAccessible.ia2TextMozilla import MozillaCompoundTextInfo
from NVDAObjects.IAccessible.ia2Web import Editor as BaseEditor
from scriptHandler import script

# Copied from the default NVDA add-on.
# @todo: Fix automatic switching to browse mode.
# It is useful when previewing Markdown documents as HTML.
class VSCodeDocument(Document):
	"""The only content in the root document node of Visual Studio code is the application object.
	Creating a tree interceptor on this object causes a major slow down of Code.
	Therefore, forcefully block tree interceptor creation.
	"""
	_get_treeInterceptorClass = NVDAObject._get_treeInterceptorClass

class CodeEditor(BaseEditor):

	# Remove states that are not needed to be announced on every focus.
	# We overwrite a default method for a control that returns states.
	def _get_states(self):
		states = super(CodeEditor, self).states
		states.discard(cTs.STATE_AUTOCOMPLETE)
		states.discard(cTs.STATE_MULTILINE)
		return states

	# Normalize and compare 2 strings.
	def compareStrings(self, currentName: str, lastName: str):
		cN = str(currentName).lower()
		lN = str(lastName).lower()
		if cN == lN:
			self.appModule.lastEditorName =cN
			return None
		else:
			self.appModule.lastEditorName = cN
			# The focus shifted to a new document and we are in a different line.
			self.appModule.fromCompletion = False
			return cN
	# Handle gain focus event for the editor.
	def event_gainFocus(self):
		# Set the name of the editor to none to preventing speakint on every focus.
		# The name of a currently opened file can be read from the window title.
		# Set the role to an empty string instead of 'edit'.
		# It will be skipped and not announced on every focus.
		# This change applies only to the main code editor.
		self.name = self.compareStrings(self.name, self.appModule.lastEditorName)
		self.roleText = str('\0')
		speech.cancelSpeech()
		super(CodeEditor,self).event_gainFocus()
		speech.cancelSpeech()
		self.processLine()

	# Handle lost focus event for the editor
	def event_loseFocus(self):
		# Set the name of the editor to none to prevent speaking on focus lose.
		# The name of a currently opened file can be read from the window title.
		self.name = None
		super(CodeEditor,self).event_loseFocus()

	# Logic for processing lines of code
	def processLine(self):
		# Cancel speech in advance.
		speech.cancelSpeech()
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
		if( self.appModule.fromCompletion == True
		or lastStartOffset == currentStartOffset
		):
			currentCursor = self.makeTextInfo(textInfos.POSITION_SELECTION)
			currentCursor._start._startOffset = currentCursor._start._endOffset
			#currentCursor.collapse()
			#currentCursor.expand(textInfos.UNIT_CHARACTER)
			speech.cancelSpeech()
			currentCursor.text = "\n"
			speech.speakTextInfo(
			currentCursor,
			textInfos.UNIT_CHARACTER,
			reason=OutputReason.FOCUS,
			suppressBlanks=True)
			return
		else:
			otherLine = self.makeTextInfo(textInfos.POSITION_SELECTION)
			otherLine.collapse()
			otherLine.expand(textInfos.UNIT_LINE)
			speech.speakTextInfo(
			otherLine,
			textInfos.UNIT_LINE,
			reason=OutputReason.FOCUS)
<<<<<<< HEAD
			self.appModule.lastOffset = otherLine._start._startOffset
=======
			self.appModule.lastStartOffset = otherLine._start._startOffset
			return

	def event_caret(self):
		super(CodeEditor, self).event_caret()
		if self is api.getFocusObject() and not eventHandler.isPendingEvents('gainFocus'):
			self.detectPossibleSelectionChange()
		tx = self.makeTextInfo(textInfos.POSITION_SELECTION).copy()
		tx.collapse()
		tx.expand(textInfos.UNIT_LINE)
		lineStart = tx._start._startOffset
		if self.appModule.lastStartOffset == lineStart:
			return
		else:
			self.appModule.lastStartOffset = lineStart
>>>>>>> 21.0
			return

# A custom list item for code completion values.
class CustomListItem(IAccessible):

	# Remove states that are not needed to be announced on every focus.
	# We overwrite a default method for a control that returns states.
	def _get_states(self):
		states = super(CustomListItem, self).states
		states.discard(cTs.STATE_SELECTABLE)
		states.discard(cTs.STATE_SELECTED)
		return states

	def event_gainFocus(self):
		speech.cancelSpeech()
		self.roleText = str('\0') # An empty string.
		self.roleTextBraille = str('\0') # An empty string.
		super(CustomListItem, self).event_gainFocus()
		# Set the flag that additionally informs we are in the same line.
		self.appModule.fromCompletion = True

	def eventlostFocus(self):
		speech.cancelSpeech()

class AppModule(appModuleHandler.AppModule):

	# This module-scoped variable holds last start offset.
	# It is declared on a module scope to not be reset within a editor class.
	lastStartOffset = 0 # It is 0 in an empty file.
	# The normalized name of the last focused editor.
	lastEditorName = "Editor" # A placeholder value.
	# A flag that specifies if the user was completing intellisense.
	fromCompletion = False

	# Initialization method called on add-on load.
	def __init__(self, *args, **kwargs):
	# It will prevent speaking the type on every focus.
		super(AppModule, self).__init__(*args, **kwargs)
		cTs.silentRolesOnFocus.add(cTs.ROLE_TREEVIEW)

	# Assign a custom list class to the code completion item only.
	def event_NVDAObject_init(self, obj):
		if(
			obj.role == cTs.ROLE_LIST
			and str(obj.name).lower() == "suggest"
			and "monaco-list" in str(obj.IA2Attributes.get("class"))
		):
			obj.name = str("\0")
			obj.roleText = str("\0")


	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(AppModule, self).chooseNVDAObjectOverlayClasses(obj, clsList)
	# Overwrite the tree interceptor class.
		if Document in clsList and obj.IA2Attributes.get("tag") == "#document":
			clsList.insert(0, VSCodeDocument)
	# Overwrite the standard editor class with a custom for Visual Studio Code.
		if( obj.windowClassName == "Chrome_RenderWidgetHostHWND"
		and obj.role == cTs.ROLE_EDITABLETEXT
		and cTs.STATE_MULTILINE in obj.states
		and 'inputarea' in str(obj.IA2Attributes.get('class'))
		and not "Source Control" in str(obj.simpleParent.name)
		):
			clsList.insert(0, CodeEditor)
		# Assign a custom list item class to the code completion item only.
		if(
			obj.role == cTs.ROLE_LISTITEM
		and 'monaco-list-row' in str(obj.IA2Attributes.get("class"))
		): 
			clsList.insert(0 , CustomListItem)

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
		cTs.silentRolesOnFocus.discard(cTs.ROLE_LIST)
