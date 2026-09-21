# ECC Integration

Zenith vendors the MIT-licensed agent, skill, and command assets from
Everything Claude Code (ECC) under `zenith/integrations/ecc/`.

The catalog is read-only. Use the `ecc_catalog`, `ecc_search`, and `ecc_get`
tools to discover and read assets. ECC agents can also be delegated by their
short name, such as `code-reviewer`; they run with Zenith's shared
collaboration tools and the imported instruction prompt.

The current import contains 68 agents, 415 Markdown skill documents, and 94
commands. Supporting skill references and scripts are retained in the vendor
tree, but Zenith does not execute them automatically.

To refresh the import, copy the upstream `agents`, `skills`, and `commands`
directories into `zenith/integrations/ecc/` and replace its `LICENSE` file.
Review the upstream license and run `pytest tests/test_ecc_catalog.py -q`
after updating.