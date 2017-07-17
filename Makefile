all:	habitica_planner/i18n/ru/LC_MESSAGES/habitica_planner.mo

habitica_planner/i18n/messages.pot: habitica_planner/*.py
	sh -c "xgettext -L python --keyword=N_ -o $@ habitica_planner/*.py"

habitica_planner/i18n/new_ru.po: habitica_planner/i18n/messages.pot habitica_planner/i18n/ru.po
	msgmerge habitica_planner/i18n/ru.po habitica_planner/i18n/messages.pot > $@

habitica_planner/i18n/ru/LC_MESSAGES/habitica_planner.mo: habitica_planner/i18n/new_ru.po
	mkdir -p habitica_planner/i18n/ru/LC_MESSAGES/
	msgfmt -o $@ $<

clean:
	rm -f habitica_planner/i18n/messages.pot habitica_planner/i18n/new_ru.po

pypi:
	python setup.py sdist upload --identity="cpp.create@gmail.com" --sign
	python setup.py bdist_wheel upload --identity="cpp.create@gmail.com" --sign
