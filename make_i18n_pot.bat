@echo off
rem python C:\Programme\Python23\Scripts\i18ndude rebuild-pot --pot i18n\eduComponent.pot --create eduComponents -s .
python C:\Programme\Python23\Scripts\i18ndude rebuild-pot --pot i18n\eduComponents.pot --create eduComponents --merge i18n\eduComponents.pot -s .
 
pause