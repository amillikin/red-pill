import requests
import os
from dotenv import load_dotenv
load_dotenv(os.environ.get("PYENV"))

# Synapse Server
API_BASE = "https://synapse.loofylabs.com/_synapse/admin/v1/registration_tokens"
SYNAPSE_SHARED_SECRET = os.getenv("SYNAPSE_SHARED_SECRET")
headers = {
    "Authorization": f"Bearer {SYNAPSE_SHARED_SECRET}"
}

# Request All Tokens (GET)
# opt param 'valid' (true/false)
# opt path params:
#   /<token> list a specific token (GET)
#   /new creates new token (POST)
#        token: The registration token. A string of no more than 64 characters that consists only of characters matched by the regex [A-Za-z0-9._~-].
#           Default: randomly generated.
#        uses_allowed: The integer number of times the token can be used to complete a registration before it becomes invalid.
#           Default: null (unlimited uses).
#        expiry_time: The latest time the token is valid. Given as the number of milliseconds since 1970-01-01 00:00:00 UTC (the start of the Unix epoch). You could use, for example, date '+%s000' -d 'tomorrow'.
#           Default: null (token does not expire).
#        length: The length of the token randomly generated if token is not specified. Must be between 1 and 64 inclusive.
#           Default: 16.
#   /<token> update a specific token (PUT)
#       uses_allowed:
#       expiry_time:
#   /<token> DELETE a specific token (DELETE)
#
#    token: The token which can be used to authenticate registration.
#    uses_allowed: The number of times the token can be used to complete a registration before it becomes invalid.
#    pending: The number of pending uses the token has. When someone uses the token to authenticate themselves, the pending counter is incremented so that the token is not used more than the permitted number of times. When the person completes registration the pending counter is decremented, and the completed counter is incremented.
#    completed: The number of times the token has been used to successfully complete a registration.
#    expiry_time: The latest time the token is valid. Given as the number of milliseconds since 1970-01-01 00:00:00 UTC (the start of the Unix epoch). To convert this into a human-readable form you can remove the milliseconds and use the date command. For example, date -d '@1625394937'.

prompt = "Please select an option: (l)ist, (c)reate, (u)pdate, (d)elete, (h)elp, (q)uit\n> "

help_prompt = """
l: [l]ist token(s) with details
    - if no parameter included, lists all
    - optionally, include space delimited list of tokens to check
c: [c]reate token
    - creates a random 16 character token that does not expire
    - optionally, prompted to include token, uses_allowed, expiry_time
u: [u]pdates token(s)
    - must include at least one token
    - may include space delimited list of all tokens to update
    - updatable: uses_allowed, expiry_time
d: [d]elete
    - must include at least one token
    - may include space delimited list of all tokens to delete
"""

mode = ""
while mode != "q":
    user_input = input(prompt).split(" ")

    if len(user_input) > 0:
        mode = user_input[0].lower()
        data = []

        if mode == "h":
            print(help_prompt)

        elif mode == "l":
            if len(user_input) == 1:
                resp = requests.get(
                    url=API_BASE,
                    headers=headers
                )
                resp.raise_for_status()
                data.append(resp.json())
            else:
                for i in range(1,len(user_input)):
                    resp = requests.get(
                        url=f"{API_BASE}/{user_input[i]}",
                        headers=headers
                    )
                    resp.raise_for_status()
                    data.append(resp.json())

        elif mode == "c":
            params = {
                "token": "",
                "uses_allowed": 0,
                "expiry_time": 0,
                "length": 0
            }
            try:
                params["token"] = input("Specify a token: ").strip()
            except ValueError as verr:
                pass  # need to catch this exception for empty input

            try:
                params["uses_allowed"] = int(input("Specify allowed number of uses (default: unlimited): ").strip())
            except ValueError as verr:
                pass  # need to catch this exception for empty input

            try:
                params["expiry_time"] = int(input("Specify a expiration time in epoch (default: never): ").strip()) * 1000

            except ValueError as verr:
                pass  # need to catch this exception for empty input

            if params["token"] == "":
                try:
                    params["length"] = int(input("Random token will be created.\n Length (default: 16): ").strip())
                except ValueError as verr:
                    pass  # need to catch this exception for empty input

            new_params = { k:v for (k,v) in params.items() if not v == "" }

            resp = requests.post(
                url=f"{API_BASE}/new",
                json=new_params,
                headers=headers
            )
            resp.raise_for_status()
            data.append(resp.json())

        elif mode == "u":
            params = {
                "uses_allowed": "",
                "expiry_time": "",
            }
            params["uses_allowed"] = input("Specify allowed number of uses (default: unlimited): ").strip()
            params["expiry_time"] = input("Specify a expiration time in epoch (default: never): ").strip()

            new_params = { k:v for (k,v) in params.items() if not v == "" }

            for i in range(1,len(user_input)):
                resp = requests.put(
                    url=f"{API_BASE}/{user_input[i]}",
                    json=new_params,
                    headers=headers
                )
                resp.raise_for_status()
                data.append(resp.json())

        elif mode == "d":
            if len(user_input) == 1:
                resp = requests.delete(
                    url=API_BASE
                )
                resp.raise_for_status()
                data.append(resp.json())
            else:
                for i in range(1,len(user_input)):
                    resp = requests.delete(
                        url=f"{API_BASE}/{user_input[i]}"
                    )
                    resp.raise_for_status()
                    data.append(resp.json())
        print(f"{data}")
    else:
        mode = ""
