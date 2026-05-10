def print_results(result):

    print("=" * 60)
    print("STAGE 1: TOKENS")
    print("=" * 60)

    print(f"{'LINE':<6} {'TYPE':<15} VALUE")

    print("-" * 40)

    for tok in result['tokens']:

        print(
            f"{tok['line']:<6} {tok['type']:<15} {tok['value']}"
        )

    print("\\n" + "=" * 60)
    print("STAGE 3: SYMBOL TABLE")
    print("=" * 60)

    if result['symbol_table']:

        print(
            f"{'NAME':<15} {'TYPE':<12} {'SCOPE':<12} INITIALIZED"
        )

        print("-" * 50)

        for sym in result['symbol_table']:

            init = "Yes" if sym['initialized'] else "No"

            print(
                f"{sym['name']:<15} "
                f"{sym['type']:<12} "
                f"{sym['scope']:<12} "
                f"{init}"
            )

    else:

        print("(no symbols declared)")

    print("\\n" + "=" * 60)
    print("STAGE 4: THREE ADDRESS CODE")
    print("=" * 60)

    if result['tac']:

        for i, line in enumerate(result['tac'], 1):

            print(f"{i:>3}: {line}")

    else:

        print("(no instructions generated)")

    print("\\n" + "=" * 60)
    print("ERRORS")
    print("=" * 60)

    if result['errors']:

        for err in result['errors']:
            print(f"*** {err}")

    else:

        print("No errors found. Compilation successful!")

    print("=" * 60)