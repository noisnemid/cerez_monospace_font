mv ~/.local/share/fonts/cerez.* ~/trash
cp cerez.*tf ~/.local/share/fonts/
# fc-cache -fv
python ./fontforge_x_version_font_generate.py
