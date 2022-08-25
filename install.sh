mkdir -p ~/.local/share/fonts/
mkdir -p ~/.trash_manual
mv ~/.local/share/fonts/cerez.* ~/.trash_manual
cp cerez.*tf ~/.local/share/fonts/
# fc-cache -fv
python ./fontforge_x_version_font_generate.py
