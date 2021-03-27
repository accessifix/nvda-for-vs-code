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
from speech import cancelSpeech
import textInfos
import ui
from logHandler import log
from NVDAObjects import NVDAObject
from NVDAObjects.IAccessible import IAccessible
from NVDAObjects.IAccessible.chromium import Document
from NVDAObjects.IAccessible import ia2Web
from NVDAObjects.IAccessible.ia2TextMozilla import MozillaCompoundTextInfo
from NVDAObjects.IAccessible.ia2Web import Editor as BaseEditor
from scriptHandler import script

# Custom control classes for widgets.
from . import electron, editor, suggestion


class AppModule(appModuleHandler.AppModule):

	# This module-scoped variable holds last start offset.
	# It is declared on a module scope to not be reset within a editor class.
	lastStartOffset = 0  # It is 0 in an empty file.
	# The normalized name of the last focused editor.
	lastEditorName = "Editor"  # A placeholder value.
	# A flag that specifies if the user was completing intellisense.
	fromCompletion = False
	# A flag that specifies if the application lost focus.
	editorLostFocus = True

	# Initialization method called on add-on load.
	# 	def __init__(self, *args, **kwargs):
	# It will prevent speaking the type on every focus.
	# 		super(AppModule, self).__init__(*args, **kwargs)
	# 		cTs.silentRolesOnFocus.add(cTs.ROLE_TREEVIEW)

	# Assign a custom list class to the code completion item only.
	def event_NVDAObject_init(self, obj):
		if obj.role == cTs.ROLE_LIST and "monaco-list" in str(obj.IA2Attributes.get("class")):
			obj.name = str("\0")
			obj.roleText = str("\0")

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(AppModule, self).chooseNVDAObjectOverlayClasses(obj, clsList)
		# Overwrite the tree interceptor class.
		if Document in clsList and obj.IA2Attributes.get("tag") == "#document":
			clsList.insert(0, electron.VSCodeDocument)
		# Overwrite the standard editor class with a custom for Visual Studio Code.
		if (
			obj.windowClassName == "Chrome_RenderWidgetHostHWND"
			and obj.role == cTs.ROLE_EDITABLETEXT
			and cTs.STATE_MULTILINE in obj.states
			and "inputarea" in str(obj.IA2Attributes.get("class"))
			and not "Source Control" in str(obj.simpleParent.name)
		):
			clsList.insert(0, editor.VSCodeEditor)
		# Assign a custom list item class to the code completion item only.
		if obj.role == cTs.ROLE_LISTITEM and "monaco-list-row" in str(
			obj.IA2Attributes.get("class")
		):
			clsList.insert(0, suggestion.VSSuggestionItem)

	# Send escape key to the application
	# we must capture escape to prevent losing focus
	def script_FixFocus(self, gesture):
		gesture.send()

	__gestures = {
		"kb:escape": "FixFocus",
	}



	# Add back TREVIEW and TREEVIEWITEM to roles spoken on focus.

	def terminate(self):
		cTs.silentRolesOnFocus.discard(cTs.ROLE_TREEVIEW)
		cTs.silentRolesOnFocus.discard(cTs.ROLE_LIST)
		# Flag that the application lost focus.
		self.editorLostFocus = True
