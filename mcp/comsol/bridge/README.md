# COMSOL Bridge Notes

This bridge uses user-owned COMSOL executables discovered by
`ai-cae-toolbox setup`.

The supported bridge path is:

1. Discover `COMSOL_ROOT`, `COMSOL_BATCH`, `COMSOL_COMPILE`, and `COMSOL_JAVA`.
2. Write or receive a COMSOL Java API model.
3. Compile with `comsolcompile`.
4. Run the compiled class through `comsolbatch`.
5. Save an `.mph` file.
6. Compile and run a small validator that loads the `.mph` through the COMSOL
   Java API.
7. Scan logs and outputs with the evidence tools.

The bridge does not bundle COMSOL libraries, manuals, or example models.
