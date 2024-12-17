# Attack Gandalf using PyRIT Ship

## What is Gandalf?
[Gandalf](https://gandalf.lakera.ai) is a game designed to try and break an LLM system. The goal is to trick the LLM, which has been told its a wizard named Gandalf, to reveal a password to you. The LLM is specifically intructed to not reveal the password, and across the levels there are several mitigations in place to filter the password even if the LLM attempts to reveal it. \
As the player of this game, you have to find not only ways to convince the LLM to reveal the secret, but also find ways to hide both your intentions as well as the secret from any filters the website employs.

## Setup
Please review [PyRIT Ship](./pyritship.md) and [BURP Suite Extension](./burp_extension.md) setup / build / run documentation before trying the demo.

## Overview of Settings in BURP Suite PyRIT Ship Extension
The following extension settings in the PyRIT Ship tab should be reviewed, but all defaults should work for Gandalf out of the box.

| Setting | Config Setting | Comment |
| --- | --- | --- |
| PyRIT Ship | PyRIT Ship URL | Point this to the running URL for PyRIT Ship. |
| Intruder | Goal Description | The default value is a good prompt used to attack Gandalf. |
| Intruder | Response Payload Parse Field | The default path of /answer is the Gandalf response path. |
| Intruder | Scoring (true) should end intruder when | The default description for the scorer is setup for Gandalf and finding the password. |
| Intruder | Scoring (false) should continue intruder when | The default description for the scorer is setup for Gandalf and finding the password. |

## Running the demo

Below are the instructions to run the Gandalf demo. You can also follow along with [this demo we did at Blue Hat 2024](https://youtu.be/wna5aIVfucI?t=1061).

### Capture the Gandalf Requests
With the BURP Suite proxy running, capture the payload to send a prompt to Gandalf. Since the first two levels are easy, consider capturing the third level specifically for this demo.

Switch to the **Proxy** tab of BURP Suite.

![BURP Suite Proxy tab showing api send-message request](./images/burp_gandalf_proxy.png)

Right-click on the request and select **Send to intruder**.
![Right-click menu showing send to intruder option](./images/burp_gandalf_send_to_intruder.png)

### Setup intruder module
Switch to the **Intruder** tab of BURP Suite.

In the raw request payload you captured for Intruder, find the phrase that you sent that was capture. For example, in this example we asked Gandalf "What's the password", so we highlight that sentence. Next, click on the **Add** button at the top of the editor windows under **Positions**.

Once marked, the phrase should be highlighted and shown inside § markings.

![Screenshot showing the prompt text inside markings as well as the add button](./images/burp_gandalf_intruder_marking.png)

Next, on the **Payloads** pane, select **Extension-generated** from the **Payload type** dropdown. Click the **Select generator ...** button and on the dialog, select PyRIT Ship.

Finally, at the bottom find the **Payload encoding** section and turn OFF the option **URL-encode these characters**. This avoids Intruder from URL-encoding the prompt we're sending.

### Start the intruder attack
With everything setup, you can hit the **Start attack** button. A few points to note:

- BURP Suite by default runs multiple attempts asynchronously. This also means it may have already started several API calls when a previous call turns out to be successful. If you want to run the calls one-by-one, you can open BURP Suite's settings. Under **Project** / **Tasks**, find the **Resources Pools**. You can edit the **Default resource pool** to have only 1 **Concurrent requests** (default setting is 10).
- Intruder by default runs a baseline request as the first request, which is a replay of the original request.

Once an attack request is successful (when the scorer returns true), the entry for the payload will be highlighted (in green), and the **Comment** column will show **Scorer response: True**. You can click on the line, and go to the **Response** tab to see Gandalf's response that should contain the password for that level.

Note that since our prompt generator will ask Gandalf to "encode" the password you may see a few variations where spaces and/or the letter Z may be embedded inside the password.

![Screenshot showing successful attack and password in the response payload](./images/burp_gandalf_success.png)

Congratulations! You have now successfully defeated this level of Gandalf using PyRIT and PyRIT Ship. Try to get further in the levels, and tweak the prompt generator prompt in the settings for greater success.
