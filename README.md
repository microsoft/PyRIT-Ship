# Introduction 
This repository contains our prototype to enable the open source [PyRIT](https://github.com/Azure/PyRIT) toolkit to be used as an API for integrating into other tooling. We welcome suggestions and feedback, and we intend to keep this repository updated. However, at this point this is a prototype and passion project for our team and have no roadmap or funding to maintain this as an actual product.

The repository currently contains:
- /pyritship : A Python Flax Server with some basic features of PyRIT exposed over API (prompt generator and scoring)
- /burp_extension : A Java extension for BURP Suite to use PyRIT from the **Intruder** module

![Cartoon image of pirate raccoons on a pirate ship](./docs/images/pyrit_ship.png)

# Blue Hat 2024 Talk
We gave [a talk at Blue Hat 2024 about PyRIT Ship](https://www.youtube.com/watch?v=wna5aIVfucI), talking about the Microsoft AI Red Team and why we made PyRIT Ship and what our hopes and dreams are. If you want to skip straight to the demo, [you can use this link](https://youtu.be/wna5aIVfucI?t=1061).

# Getting Started - Setup & Build code
[PyRIT Ship Setup & Documentation](/docs/pyritship.md) \
[BURP Suite Extension Setup & Documentation](/docs/burp_extension.md)

# Demo running BURP Suite extension
[Attack Gandalf with PyRIT Ship](/docs/burp_gandalf_demo.md)

# TODO
We have code close to ready to support:
- Running PyRIT Ship in a Docker container so no local Python setup is required
- Using Entra ID auth for Azure OpenAI (PyRIT supports this, but PyRIT Ship only uses API key at the moment)
- Using other endpoints besides Azure OpenAI (PyRIT supports this, we just need to add this to PyRIT Ship)
- Prompt generation conversation history

Work-in-progress:
- Browser extension (Chrome/Edge)
- Supporting converters in BURP Suite

Wishlist:
- More PyRIT features in the API
- [Playwright](https://playwright.dev/) integration to support test automation using PyRIT Ship / PyRIT


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.