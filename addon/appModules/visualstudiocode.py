# NVDA Add-on for Microsoft Visual studio Code
# Author: Pawel Urbanski <pawel@pawelurbanski.com>, under GPL licence.
# Contains shared code imported by release specific modules.
import appModuleHandler
import eventHandler
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

	def event_gainFocus(self) :
		super(VSCodeEditor, self).event_gainFocus()
		TextInfo = MozillaCompoundTextInfo
		ti = self.makeTextInfo(textInfos.POSITION_SELECTION)
		ti.expand(textInfos.UNIT_LINE)
		self.processLine(ti)

# NVDA was reading the entire line after every code completion.
# This script handler reports last completed item.
# It is triggered by the enter key for caret event is not fired.
# There is one issue: last item is sometimes read when moving to the next line.
# It happens when you scroll back up and to the end of line and hit enter moving to the next line.

	def script_HandleInteliSense(self, gesture):
		gesture.send()
		TextInfo = MozillaCompoundTextInfo
		ti = self.makeTextInfo(textInfos.POSITION_SELECTION)
		ti.collapse()
		ti.expand(textInfos.UNIT_LINE)
		self.processLine(ti)
	__gestures = {
		"kb:enter":"HandleInteliSense",
	}

	def processLine(self, ti):
		self.appModule.PrevStartOffset = ti._start._startOffset
		self.appModule.PrevEndOffset = ti._start_endOffset
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
		# If old and current startOffsets are different we moved to a new line
		if not os == cs:
			# Prevent reading editor group info after moving to next line
			# Script does it only after recent completion.
			# Scrolling up and down through the code works well.
			self.name = "" 
			# Update offset values
			self.appModule.PrevStartOffset = curr._start._startOffset
			self.appModule.PrevEndOffset = curr._start_endOffset
		# If we are in teh same line, do not read the entire line
		elif os == cs:
			# We are in the same line, so read only inserted item.
			# Do not read the line from the beginning.
			# Read back what was inserted by the user
			TextInfo = MozillaCompoundTextInfo
			line = self.makeTextInfo(textInfos.POSITION_SELECTION)
			line.collapse()
			line.expand(textInfos.UNIT_WORD)
			speech.cancelSpeech()
			speech.speakTextInfo(line,textInfos.UNIT_WORD, reason=controlTypes.REASON_CHANGE, suppressBlanks=True)

class AppModule(appModuleHandler.AppModule):
	PrevStartOffset = 0
	PrevEndOffset = 0

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(AppModule, self).chooseNVDAObjectOverlayClasses(obj, clsList)
		if obj.windowClassName == "Chrome_RenderWidgetHostHWND" and obj.role == controlTypes.ROLE_EDITABLETEXT:
			clsList.insert(0, VSCodeEditor)

	def script_FixFocus(self, gesture):
		gesture.send()
	__gestures = {
		"kb:escape":"FixFocus",
	}
