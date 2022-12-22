from itertools import chain
# https://github.com/dmort27/panphon
from panphon import FeatureTable
from panphon.segment import Segment
import re
from typing import Union

DEBUG = False

SYLLABLE_BREAK = '.'
PRIMARY_STRESS = 'ˈ'
SECONDARY_STRESS = 'ˌ'
STRESSES = [PRIMARY_STRESS, SECONDARY_STRESS]

ft = FeatureTable()

voiceless_stops = ['p', 'p̪', 't̼', 't', 'ʈ', "c", 'k', 'q', 'ʡ', 'ʔ']
voiced_stops = ['b', 'b̪', 'd̼', 'd', 'ɖ', 'ɟ', 'ɡ', 'ɢ',]
voiceless_stops_intersection = ft.fts_intersection(voiceless_stops)
voiced_stops_intersection = ft.fts_intersection(voiced_stops)
stops = voiced_stops + voiceless_stops
stops_intersection = ft.fts_intersection(stops)
approximants = ['ʋ', 'ɹ', 'ɻ', 'j', 'ɰ', 'ʔ̞']
approximants_intersection = ft.fts_intersection(approximants)
# silibant + non-silibant
voiceless_silibant_fricatives = ['s', 'ʃ', 'ʂ', 'ɕ',]
voiceless_silibant_fricatives_intersections = ft.fts_intersection(voiceless_silibant_fricatives)
voiceless_non_silibant_fricatives = ['ɸ', 'f', 'θ̼', 'θ', 'θ̠', 'ɹ̠̊˔', 'ɻ̊˔', 'ç', 'x', 'χ', 'ħ', 'h', ]
voiceless_non_silibant_fricatives_intersection = ft.fts_intersection(voiceless_non_silibant_fricatives)
voiceless_fricatives = voiceless_silibant_fricatives + voiceless_non_silibant_fricatives
voiced_fricatives = ['z', 'ʒ', 'ʐ', 'ʑ', 'β', 'v', 'ð̼', 'ð', 'ð̠', 'ɹ̠˔', 'ɻ˔', 'ʝ', 'ɣ', 'ʁ', 'ʕ', 'ɦ']
voiceless_fricatives_intersection = ft.fts_intersection(voiceless_fricatives)
voiced_fricatives_intersection = ft.fts_intersection(voiced_fricatives)

# https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart_for_English_dialects#Chart
AAVE_DIPTHONGS = ["ɛə", "eə", "ɒɔ", "ɔʊ", "iə", "ɛɪ", "eɪ", "eə", "ʊu", "ʊu", "äɪ", "äe", "ʌʊ", "ɔʊ", "æɔ", "æə", "iə", "iɤ", "ɛə", "oə", "ɔə", "ɔo", "uə", "ʊə",]
GENERAL_AMERICAN_DIPTHONGS = ["eə", "ɛə", "eɪ", "ɛɪ", "ɪi", "eɪ", "ʊu", "ʉu", "äɪ", "aɪ", "æɪ", "aɪ", "äɪ", "ʌɪ", "ɜɪ", "ɐɪ", "ɔɪ", "oɪ", "oʊ", "ʌʊ", "ɔʊ", "äʊ", "aʊ", "æʊ"]
GENERAL_AUSTRALIAN_DIPTHONGS = ["ɪi", "ɪi", "əi", "ɛɪ", "æɪ", "ɐɪ", "ɐɪ", "äɪ", "ʊu", "ʊ̈ʉ", "ʊ̈ʉ", "əʉ", "ʊu", "ʊ̈ʉ", "ʊ̈ʉ", "əʉ", "äɪ", "ɑe", "ɑe", "ɑe", "ɒe", "oɪ", "ɜʉ", "ɐʉ", "ɐʉ", "äʉ", "ɒʊ", "ɔʊ", "aɔ", "ao", "æɔ", "æo", "æo", "æə", "ɛo", "ɛə", "ɪə", "iə", "iə", "iə", "eə", "eə", "ʊ̈ʉə", ]
MANCHESTER_ENGLISH_DIPTHONGS = ["ɪi", "ɛɪ", "eɪ", "ʊu", "aɪ", "äɪ", "ɔɪ", "ɔʊ", "ɔo", "ɪə", "ʊə", 'əʊ']

DIPTHONGS = {'ɔɪ', 'eə', 'ɜʉ', 'ɑe', 'æɪ', 'ʉu', 'äʉ', 'ɛə', 'äe', 'ɛo', 'ʌɪ', 'aʊ', 'oə', 'ɪi', 'ɔə', 'äʊ', 'ʊ̈ʉ', 'ɐʉ', 'æə', 'ɜɪ', 'əi', 'ɪə', 'iɤ', 'eɪ', 'aɔ', 'ao', 'æʊ', 'ʌʊ', 'əʉ', 'ɔo', 'ʊu', 'ʊə', 'ʊ̈ʉə', 'æo', 'ɒe', 'uə', 'ɐɪ', 'ɔʊ', 'äɪ', 'ɒʊ', 'ɛɪ', 'aɪ', 'oʊ', 'iə', 'ɒɔ', 'æɔ', 'oɪ', 'əʊ'}
# DIPTHONGS = set(AAVE_DIPTHONGS + GENERAL_AMERICAN_DIPTHONGS + GENERAL_AUSTRALIAN_DIPTHONGS + MANCHESTER_ENGLISH_DIPTHONGS)
# print(DIPTHONGS)
# print(DIPTHONGS.issuperset({"oʊ", "aʊ", "aɪ", "eɪ", "ɔɪ"}))

# Apparently, I'm creating a comprehensive list of IPA vowels now
random_vowels = [
	'ɝ', # staffordshire's /ˈstæfɝdʃɝz/
]
thongs = '|'.join(list(DIPTHONGS) + ft.all_segs_matching_fts({'syl': 1}) + random_vowels)
ENGLISH_IPA_VOWELS = re.compile(r'(' + thongs + '):?', re.UNICODE)

def split_before(string: str, separator: str) -> list[str]:
	"""
	Split {string} on {separator} but include {separator}.
	"""
	split = string.split(separator)
	add_separator_back = [separator + part if index > 0 else part for (index, part) in enumerate(split)]
	return [part for part in add_separator_back if part]

def initial_pass(pronunciation: str) -> list[str]:
	"""
	https://en.wikipedia.org/wiki/English_phonology#Syllable_structure
	https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
	Occasionally the stress mark is placed immediately before the
	nucleus of the syllable, after any consonantal onset.
	In such transcriptions, the stress mark does not mark a syllable boundary.
	⟨.⟩ for a syllable break
	⟨ˈ ˌ⟩ for primary and secondary stresses (appears before stressed syllable)
	⟨ˈˈ or ˌˌ⟩ for extra-{strong,weak} stress
	"""
	no_slashes = pronunciation[1:-1]
	# NOTE: All optional phones are made required
	# TODO: Support optional phones
	no_parentheses = no_slashes.replace("(", '').replace(")", '')
	split_on_breaks = no_parentheses.split(SYLLABLE_BREAK)
	split_on_extra_strong_stress = split_on_primary_stress = list(chain.from_iterable(
		split_before(part, PRIMARY_STRESS + PRIMARY_STRESS) for part in split_on_breaks
	))
	split_on_extra_weak_stress = list(chain.from_iterable(
		split_before(part, SECONDARY_STRESS + SECONDARY_STRESS) for part in split_on_extra_strong_stress
	))
	split_on_primary_stress = list(chain.from_iterable(
		split_before(part, PRIMARY_STRESS) for part in split_on_extra_weak_stress
	))
	split_on_secondary_stress = list(chain.from_iterable(
		split_before(part, SECONDARY_STRESS) for part in split_on_primary_stress
	))

	return split_on_secondary_stress

def maybe_match(segment: str, features: Union[dict, Segment]) -> bool:
	parsed = ft.fts(segment)
	if parsed != None:
		return parsed.match(stops_intersection)
	else:
		return False


def destructure_syllables(parts: list[str]) -> list[str]:
	"""
	https://linguistics.stackexchange.com/questions/30933/how-to-split-ipa-spelling-into-syllables
	TODO: Document this beast.
	"""
	return_value = []

	for part in parts:
		if DEBUG: print('Initial part', part)
		vowels = sorted(ENGLISH_IPA_VOWELS.finditer(part), key=lambda group: group.start(0), reverse=True)
		if len(vowels) <= 1:
			if DEBUG: print('One or no vowels')
			return_value.append(part)
			continue

		syllables = []
		end = len(part)

		for index, vowel in enumerate(vowels, start=1):
			parsed = ''

			if index == len(vowels):
				if DEBUG: print('First syllable')
				parsed = part[:end]
				end = 0
			else:
				vowel_text = vowel.group(0)
				vowel_start = vowel.start(0)
				vowel_end = vowel.end(0)

				behind_one = part[vowel_start - 1]
				behind_two = part[vowel_start - 2 : vowel_start]
				behind_three = part[vowel_start - 3 : vowel_start]


				if not parsed and behind_three and behind_three[0] not in STRESSES:
					reason = ""
					# /s/ plus voiceless stop plus approximant
					if (
						behind_three[0] == 's'
						and maybe_match(behind_three[1], voiceless_stops_intersection)
						and maybe_match(behind_three[2], approximants_intersection)
					):
						reason = '/s/ plus voiceless stop plus approximant'
					# /s/ plus nasal plus approximant
					elif (
						behind_three[0] == 's'
						and maybe_match(behind_three[1], {'nas': 1})
						and maybe_match(behind_three[2], approximants_intersection)
					):
						reason = '/s/ plus nasal plus approximant'
					# /s/ plus voiceless non-sibilant fricative plus approximant
					elif (
						behind_three[0] == 's'
						and maybe_match(behind_three[1], voiceless_non_silibant_fricatives_intersection)
						and maybe_match(behind_three[2], approximants_intersection)
					):
						reason = "/s/ plus voiceless non-sibilant fricative plus approximant"
					
					if reason:
						if DEBUG: print(reason)
						parsed = behind_three + vowel_text + part[vowel_end:end]
						end = vowel_start - 3

				if not parsed and behind_two and behind_two[0] not in STRESSES:
					reason = ''			
					# Stop plus approximant other than /j/
					if (
						behind_two[1] != 'j'
						and maybe_match(behind_two[0], stops_intersection)
						and maybe_match(behind_two[1], approximants_intersection)
					):
						reason = "Stop plus approximant other than /j/"
					# Voiceless fricative or /v/ plus approximant other than /j/
					elif (
						behind_two[1] != 'j'
						and maybe_match(behind_two[0], voiced_fricatives_intersection)
						and maybe_match(behind_two[1], approximants_intersection)
					):
						reason = "Voiceless fricative or /v/ plus approximant other than /j/"
					# Consonant other than /r/ or /w/ plus /j/ (before /uː/ or its modified/reduced forms)
					elif (
						behind_two[0] not in ['r', 'w']
						and behind_two[1] == 'j'
					):
						reason = "Consonant other than /r/ or /w/ plus /j/ (before /uː/ or its modified/reduced forms)"
					# /s/ plus voiceless stop
					elif (
						behind_two[0] == 's'
						and maybe_match(behind_two[1], voiceless_stops_intersection)
					):
						reason = "Consonant other than /r/ or /w/ plus /j/ (before /uː/ or its modified/reduced forms)"
					# /s/ plus nasal other than /ŋ/
					elif (
						behind_two[1] != 'ŋ'
						and behind_two[0] == 's'
						and maybe_match(behind_two[1], {'nas': 1})
					):
						reason = "/s/ plus nasal other than /ŋ/"
					# /s/ plus voiceless non-sibilant fricative
					elif (
						behind_two[0] == 's'
						and maybe_match(behind_two[1], voiceless_non_silibant_fricatives_intersection)
					):
						reason = "/s/ plus voiceless non-sibilant fricative"

					if reason:
						if DEBUG: print(reason)
						parsed = behind_two + vowel_text + part[vowel_end:end]
						end = vowel_start - 2

				# All single-consonant phonemes except /ŋ/
				if not parsed and behind_one and behind_one != 'ŋ':
					if DEBUG: print('All single-consonant phonemes except /ŋ/')
					parsed = behind_one + vowel_text + part[vowel_end:end]
					end = vowel_start - 1
				else:
					if DEBUG: print("No onset")
					parsed = vowel_text + part[vowel_end:end]
					end = vowel_start
			if DEBUG: print(parsed)
			syllables.insert(0, parsed)

		return_value += syllables

	return return_value

class Pronunciation:
	pronunciation: str
	original_pronunciation: str
	syllables = list[str]

	def __init__(self, pronunciation: str) -> None:
		self.original_pronunciation = pronunciation
		
		initial = initial_pass(pronunciation)
		destructured = destructure_syllables(initial)
		self.syllables = destructured 

		self.pronunciation = Pronunciation.render_syllables(destructured)

		# assert len(self.pronunciation) >= len(self.original_pronunciation)

	@staticmethod
	def render_syllables(syllables: list[str]):
		"""
		Convert a list of IPA syllables to a properly-formated IPA pronunciation.
		"""
		final = ''
		for index, syllable in enumerate(syllables):
			if (
				index != 0
				and not syllable.startswith(PRIMARY_STRESS)
				and not syllable.startswith(SECONDARY_STRESS)
			):
				final += SYLLABLE_BREAK
			final += syllable

		return final

	def __repr__(self) -> str:
		return f'<Pronunciation {self.pronunciation=}, {self.original_pronunciation=}, {self.syllables=}>'

	def __str__(self) -> str:
		return f'/{self.pronunciation}/ (from {self.original_pronunciation})'
	
	def __hash__(self) -> int:
		return hash(self.pronunciation)

if __name__ == "__main__":
	tuba = '/ˈtu.bə/'
	psych = '/saɪˈkɒlədʒɪ/'
	secondary = '/ˈsɛkənˌdɛɹi/'
	pneumonoultramicroscopicsilicovolcanoconiosis = '/njuːˌmɒ.nəʊ.ʌl.tɹə.maɪ.kɹəʊˈskɒ.pɪkˌsɪ.lɪ.kəʊ.vɒl.keɪ.nəʊ.kəʊ.niˈəʊ.sɪs/'
	cheeseburgers = "/ˈtʃizbɝɡɝz/"
	staffordshires = "/ˈstæfɝdʃɝz/"
	# print(Pronunciation(psych))
	# print(Pronunciation(tuba))
	# print(Pronunciation(secondary))
	# print(Pronunciation(pneumonoultramicroscopicsilicovolcanoconiosis))
	print(Pronunciation(cheeseburgers))
	print(Pronunciation(staffordshires))

# All single-consonant phonemes except /ŋ/
# ʒɪ
# All single-consonant phonemes except /ŋ/
# ləd
# All single-consonant phonemes except /ŋ/
# kɒ
# saɪˈkɒlədʒɪ

# Oh no, /l/ is a valid onset *and* coda,
# but it should be with /'kal/!
# What's a guy to do...
# Mr. N says I may just need to pick on or the other.
# There's got to be a better way, though...
# For now, I'm just going to leave it be.
 
# I did it! 
# We'll keep everything below for context.
# For pneumonoultramicroscopicsilicovolcanoconiosis:
# nəʊ -> n.əʊ
# Gotta add all those vowels and dipthongs:
# https://en.wikipedia.org/wiki/International_Phonetic_Alphabet_chart_for_English_dialects#Chart
# AAVE, GAE, British English, Australian
