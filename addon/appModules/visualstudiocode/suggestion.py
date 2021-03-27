from NVDAObjects.IAccessible import IAccessible
from logHandler import log
import controlTypes
import speech

# A custom list item for code completion values.
class VSSuggestionItem(IAccessible):
	# Assign the role to application for it is silenced on focus.
	# It is alsow not displayed in braille.
	role = controlTypes.ROLE_MENUITEM

	# Remove selected state to make speaking faster.
	def _get_states(self):
		states = super(VSSuggestionItem, self).states
		states.discard(controlTypes.STATE_SELECTED)
		return states

	def event_loseFocus(self):
		speech.cancelSpeech()
# A custom list for code completion values.
class VSSuggestionList(IAccessible):
	# Replace: 'Suggest' prefix in code completion list with an empty string.
	name = str("\0")
	# Replace the standard spoken list role with an empty string.
	roleText = str("\0")
