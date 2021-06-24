on run {x, y, width, height}
	tell application "System Events" to tell (first process whose frontmost = true)
		tell window 1
			set {position, size} to {{x, y}, {width, height}}
		end tell
	end tell
end run