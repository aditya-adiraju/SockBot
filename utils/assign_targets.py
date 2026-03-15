# Right now, I just manually generate the player assignments and manually edit the DB
# I should just write a helper admin function to do this work for me...
# list of discord IDs
PLAYERS = []

# There's a better way to leeetcode this.
# Our goal is to create exactly ONE cycle is our player - target graph
assignments = []
targets = set(PLAYERS)
p = targets.pop()
last_target = p
while len(targets) > 0:
    t = targets.pop()
    assignments.append((p, t))
    p = t
assignments.append((p, last_target))
