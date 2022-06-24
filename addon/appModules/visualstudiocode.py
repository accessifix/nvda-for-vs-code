# Author: Pawel Urbanski <support@accessifix.com> under GPL licence.
# Contains shared code imported by release specific modules.
# NVDA Add-on for Microsoft Visual studio Code

import api
import appModuleHandler
import braille
import controlTypes
import eventHandler
import IAccessibleHandler
import keyboardHandler
import oleacc
import speech
import textInfos
import ui
from controlTypes import OutputReason, Role, State
from logHandler import log
from NVDAObjects import NVDAObject
from NVDAObjects.IAccessible import IAccessible
from NVDAObjects.IAccessible import chromium as Electron
from NVDAObjects.IAccessible import ia2Web
from NVDAObjects.IAccessible.chromium import Document
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
		states.discard(State.AUTOCOMPLETE)
		states.discard(State.MULTILINE)
		return states

	def _get_name(self):
		name = super(CodeEditor, self).name
		if name:
			if name.lower() == self.appModule.lastEditorName.lower():
				return None
			else:
				return name
		self.appModule.lastEditorName = name

	# Handle gain focus event for the editor.
	def event_gainFocus(self):
		# Set the role label text for braille to an empty string.
		self.roleText = str('\0')
		super(CodeEditor,self).event_gainFocus()
		# Cancel speech to prevent reading the line after every completion.
		speech.cancelSpeech()
		# Read selected item after focusing the editor.
		# It covers case like switching from problems panel.
		CurrentLine = self.makeTextInfo(textInfos.POSITION_SELECTION)
		if not CurrentLine.isCollapsed:
			CurrentLine.expand(textInfos.UNIT_WORD)
			ui.message(CurrentLine.text)

	# Handle lost focus event for the editor
	def event_loseFocus(self):
		super(CodeEditor,self).event_loseFocus()
		# Set the name of the editor to none to prevent speaking on focus lose.
		# The name of a currently opened file can be read from the window title.
		#self.name = None

# A custom list item for code completion values.
class CustomListItem(IAccessible):

	# Remove states that are not needed to be announced on every focus.
	# We overwrite a default method for a control that returns states.
	def _get_states(self):
		states = super(CustomListItem, self).states
		states.discard(State.SELECTABLE)
		states.discard(State.SELECTED)
		return states

	def event_gainFocus(self):
		# Set the role label text for braille to an empty string.
		self.roleTextBraille = str('\0')
		super(CustomListItem, self).event_gainFocus()

	def event_lostFocus(self):
		speech.cancelSpeech()

class AppModule(appModuleHandler.AppModule):

	# Initialization method called on add-on load.
	def __init__(self, *args, **kwargs):

	# It will prevent speaking the type on every focus.
		super(AppModule, self).__init__(*args, **kwargs)
		controlTypes.silentRolesOnFocus.add(Role.TREEVIEW)
	# It is declared on a module scope to not be reset within a editor class.
	# The normalized name of the last focused editor.
		self.lastEditorName = "Editor" # A placeholder value.

	# Assign a custom list class to the code completion item only.
	def event_NVDAObject_init(self, obj):
		if(
			obj.role == Role.LIST
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
		and obj.role == Role.EDITABLETEXT
		and State.MULTILINE in obj.states
		and 'inputarea' in str(obj.IA2Attributes.get('class'))
		and not "Source Control" in str(obj.simpleParent.name)
		):
			clsList.insert(0, CodeEditor)
		# Assign a custom list item class to the code completion item only.
		if(
			obj.role == Role.LISTITEM
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
		controlTypes.silentRolesOnFocus.discard(Role.TREEVIEW)
