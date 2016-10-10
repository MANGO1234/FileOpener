# ported from
# https://github.com/forrestthewoods/lib_fts/blob/master/code/fts_fuzzy_match.js

# Returns (bool, score, formattedStr)
# bool: True if each character in pattern is found sequentially within str
# score: integer; higher is better match. Value has no intrinsic meaning. Range varies with pattern.
#        Can only compare scores with same search pattern.
# formattedStr: input str with matched characters marked in <b> tags.


def fuzzy_match(pattern, string):
    # Score consts
    adjacency_bonus = 5                # bonus for adjacent matches
    separator_bonus = 10               # bonus if match occurs after a separator
    camel_bonus = 10                   # bonus if match is uppercase and prev is lower
    # penalty applied for every letter in string before the first match
    leading_letter_penalty = -3
    max_leading_letter_penalty = -9    # maximum penalty for leading letters
    unmatched_letter_penalty = -1      # penalty for every letter that doesn't matter

    # Loop variables
    score = 0
    patternIdx = 0
    patternLength = len(pattern)
    strIdx = 0
    strLength = len(string)
    prevMatched = False
    prevLower = False
    prevSeparator = True       # True so if first letter match gets separator bonus

    # Use "best" matched letter if multiple string letters match the pattern
    bestLetter = None
    bestLower = None
    bestLetterIdx = None
    bestLetterScore = 0

    matchedIndices = []

    # Loop over strings
    while strIdx != strLength:
        patternChar = pattern[
            patternIdx] if patternIdx != patternLength else None
        strChar = string[strIdx]

        patternLower = patternChar.lower() if patternChar != None else None
        strLower = strChar.lower()
        strUpper = strChar.upper()

        nextMatch = patternChar and patternLower == strLower
        rematch = bestLetter and bestLower == strLower

        advanced = nextMatch and bestLetter
        patternRepeat = bestLetter and patternChar and bestLower == patternLower
        if advanced or patternRepeat:
            score += bestLetterScore
            matchedIndices.append(bestLetterIdx)
            bestLetter = None
            bestLower = None
            bestLetterIdx = None
            bestLetterScore = 0

        if nextMatch or rematch:
            newScore = 0

            # Apply penalty for each letter before the first pattern match
            # Note: std::max because penalties are negative values. So max is
            # smallest penalty.
            if patternIdx == 0:
                penalty = max(strIdx * leading_letter_penalty,
                              max_leading_letter_penalty)
                score += penalty

            # Apply bonus for consecutive bonuses
            if prevMatched:
                newScore += adjacency_bonus

            # Apply bonus for matches after a separator
            if prevSeparator:
                newScore += separator_bonus

            # Apply bonus across camel case boundaries. Includes "clever"
            # isLetter check.
            if prevLower and strChar == strUpper and strLower != strUpper:
                newScore += camel_bonus

            # Update patter index IFF the next pattern letter was matched
            if nextMatch:
                patternIdx = patternIdx + 1

            # Update best letter in string which may be for a "next" letter or a
            # "rematch"
            if newScore >= bestLetterScore:

                # Apply penalty for now skipped letter
                if bestLetter != None:
                    score += unmatched_letter_penalty

                bestLetter = strChar
                bestLower = bestLetter.lower()
                bestLetterIdx = strIdx
                bestLetterScore = newScore

            prevMatched = True
        else:
            # Append unmatch characters
            # formattedStr += strChar

            score += unmatched_letter_penalty
            prevMatched = False

        # Includes "clever" isLetter check.
        prevLower = strChar == strLower and strLower != strUpper
        prevSeparator = strChar == '_' or strChar == ' '

        strIdx = strIdx + 1

    # Apply score for last match
    if bestLetter:
        score += bestLetterScore
        matchedIndices.append(bestLetterIdx)

    # Finish out formatted string after last pattern matched
    # Build formated string based on matched letters
    formattedStr = ""
    lastIdx = 0
    for i in range(0, len(matchedIndices)):
        idx = matchedIndices[i]
        formattedStr += string[lastIdx:idx] + "<b>" + string[int(idx)] + "</b>"
        lastIdx = idx + 1
    formattedStr += string[lastIdx:len(string)]

    matched = patternIdx == patternLength
    return (matched, score, string, formattedStr)


def fuzzy_filter(pattern, strings, details = False):
    strings = [fuzzy_match(pattern, s) for s in strings]
    strings.sort(reverse=True)
    if details:
        return strings
    else:
        return [s[2] for s in strings]
