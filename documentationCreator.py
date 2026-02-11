from math import ceil

types = {
    "S": ["Section heading","#=#","#   /*/   #","#=#"]
}

while True:
    type = input("Type in the type of text you'd like to nicen:\n   "+"\n   ".join([f"{key} - {value[0]}" for key, value in types.items()])+"\n> ").capitalize()
    if type in types:
        print()
        break
    else:
        print(f"Type {type} not found, please try again\n")

while True:
    text = input("Type in the text you'd like to nicen:\n> ")
    confirm = input(f"Would you like to nicen \"{text}\"? [Y/n] ").strip()
    if confirm == "":
        print()
        break
    elif confirm.lower()[0] == "y":
        print()
        break
    else:
        print()

print("COPY BELOW THIS LINE:")
text = types[type][2].replace("/*/", text)

prefix = types[type][1][0] + types[type][1][1:-1]*(ceil(len(text)/len(types[type][1][1:-1]))-2) + types[type][1][-1]
suffix = types[type][3][0] + types[type][3][1:-1]*(ceil(len(text)/len(types[type][3][1:-1]))-2) + types[type][3][-1]

print(f"{prefix}\n{text}\n{suffix}\n")