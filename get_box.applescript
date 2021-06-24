tell application "System Events" to tell (first process whose frontmost = true)
	tell window 1
          get {position, size}
	end tell
end tell