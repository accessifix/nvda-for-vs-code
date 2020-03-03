# NVDA Add-on for Microsoft Visual studio Code
# Author: Pawel Urbanski <support@accessifix.com>, under GPL licence.
# Contains shared code imported by release specific modules.
import appModuleHandler
import eventHandler
import keyboardHandler
import speech
from comtypes import COMError
import oleacc
import api
import controlTypes
import textInfos
import IAccessibleHandler
from NVDAObjects.IAccessible import IAccessible
from NVDAObjects.IAccessible import ia2Web
from NVDAObjects.IAccessible.ia2TextMozilla import MozillaCompoundTextInfo
import ui
from NVDAObjects.IAccessible.ia2Web import Editor as BaseEditor
from scriptHandler import script

class VSCodeEditor(BaseEditor):

	# Handle gain focus event for the editor.
	def event_gainFocus(self):
		super(VSCodeEditor,self).event_gainFocus()
		self.processLine()
# Handle reading out just an inserted item.
# It is triggered by the enter key for caret event is not fired.
	def script_HandleInteliSense(self, gesture):
		gesture.send()
		self.processLine()
	__gestures = {
		"kb:enter":"HandleInteliSense",
	}

	# Logic for processing lines of code
	def processLine(self):
		# Get the textInfo object for a current line
		TextInfo = MozillaCompoundTextInfo
		curr = self.makeTextInfo(textInfos.POSITION_SELECTION)
		curr.collapse()
		curr.expand(textInfos.UNIT_LINE)
		# Assign short variables for later conditions
		cs = curr._start._startOffset # Current line startOffset
		ce = curr._start._endOffset # Current line end offset
		os = self.appModule.PrevStartOffset # startOffset from previous invocation
		oe = self.appModule.PrevEndOffset # End offset from previous invocation

		# If we are in the same line, do not read the entire line
			# Do not read the line from the beginning.
			# Read back the inserted completion item.
		if os == cs:
			TextInfo = MozillaCompoundTextInfo
			insertedItem = self.makeTextInfo(textInfos.POSITION_SELECTION)
			insertedItem.collapse()
			insertedItem.expand(textInfos.UNIT_WORD)
			speech.cancelSpeech()
			speech.speakTextInfo(insertedItem,textInfos.UNIT_WORD, reason=controlTypes.REASON_FOCUS, suppressBlanks=True)
			insertedItem.collapse()
			insertedItem.expand(textInfos.UNIT_LINE)
			# Updae global text offsets
			self.appModule.PrevStartOffset = insertedItem._start._startOffset
			self.appModule.PrevEndOffset = insertedItem._start._endOffset
		else:
			TextInfo = MozillaCompoundTextInfo
			currentLine = self.makeTextInfo(textInfos.POSITION_SELECTION)
			currentLine.collapse()
			currentLine.expand(textInfos.UNIT_LINE)
			speech.cancelSpeech()
			speech.speakTextInfo(currentLine,textInfos.UNIT_LINE, reason=controlTypes.REASON_FOCUS, suppressBlanks=True)
			# Update offset values	
			self.appModule.PrevStartOffset = currentLine._start._startOffset
			self.appModule.PrevEndOffset = currentLine._start._endOffset

class AppModule(appModuleHandler.AppModule):
	# Global variables used to control line character offsets
	PrevStartOffset = 0
	PrevEndOffset = 0

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(AppModule, self).chooseNVDAObjectOverlayClasses(obj, clsList)
		if obj.windowClassName == "Chrome_RenderWidgetHostHWND" and obj.role == controlTypes.ROLE_EDITABLETEXT:
			clsList.insert(0, VSCodeEditor)

	# Send escape key when for example quitting code completion
	def script_FixFocus(self, gesture):
		gesture.send()
	__gestures = {
		"kb:escape":"FixFocus",
	}
	# Prevent repeat reading edito type of main eidtor window
	controlTypes.silentRolesOnFocus.add(controlTypes.ROLE_EDITABLETEXT)
	controlTypes.silentRolesOnFocus.add(controlTypes.ROLE_TREEVIEW)
