# Contributing
Pull requests are welcome.

## Localization
You can write a localization file for your language. Run
```
make
msginit -i habitica_planner/i18n/messages.pot -o habitica_planner/i18n/yourlang.po
```
Then edit `habitica_planner/i18n/yourlang.po` with translations where `yourlang` is two-letter language code.
After that add these lines to `Makefile`
```
habitica_planner/i18n/new_yourlang.po: habitica_planner/i18n/messages.pot habitica_planner/i18n/yourlang.po
	msgmerge habitica_planner/i18n/yourlang.po habitica_planner/i18n/messages.pot > $@

habitica_planner/i18n/yourlang/LC_MESSAGES/habitica_planner.mo: habitica_planner/i18n/new_yourlang.po
	mkdir -p habitica_planner/i18n/yourlang/LC_MESSAGES/
	msgfmt -o $@ $<
```
Please replace `yourlang` with actual language code. Also add `habitica_planner/i18n/yourlang/LC_MESSAGES/habitica_planner.mo` to `all` target.
After that you can run make and get a binary `mo` file with your translation, then you can install the package to test your localization.

### Localization update
If there is a change in localization strings, you should run `make` again to get merged `habitica_planner/i18n/new_yourlang.po` then copy that over your `habitica_planner/i18n/yourlang.po`.  A
