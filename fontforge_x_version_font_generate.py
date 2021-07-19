"""
fontforge x version font exporting

1.  What is an x version font?

    In one word, an x version font is a font whose em-size's width-height ratio is 1:2, esp. compared to its original version.

2.  Why to make an x version font?

    When using reStructuredText, Markdown or other markup languages to write docs with table formats in it, monospace fonts with a EM-width-height ratio not equal to 1:2 will get messed up with CJK fonts.

    After some digging, I found that Microsoft Visual Studio Code has a issue with rendering fonts, see the issue:
    
        https://github.com/microsoft/vscode/issues/116997

    (and there are many similar issues related to font rendering things).

    It's said that all font rendering in the editor is delegated to Chromium, and this is an upstream issue.
    
    But I don't think chromium will resolve this issue quickly.
    So I figure out an alternative:

    By using the font-fallback mechanics, set the font config of VSCode to:

        your_monospace_font, fallback,CJK_font, etc.,...

    vscode will render characters in a fallback order.

    BTW, VSCode could set individual fonts for every different language, e.g:

        "[restructuredtext]": {
            "editor.fontFamily": "'your_font','Noto Serif CJK SC'",
            "editor.fontSize": 21
        }


3.  Is there any side-effects?

    Yes.
    The x version will be a little thinner than the original font when they are set to the same font size, and the factor could be precisely calculated.

    You could consider that in both directions(x,y) the line width is shrunk to by a value, which is:

        1 - old_em /new_em

4.  ffxcfg.yml format:

        SOURCE_FILE: ./better_rel_path.sfd
        PRESET_HARD_CODED_UNDERLINE_THICKNESS: 91
        NEW_FONT_NAME: you_font_new_name

5.  references:

    https://fontforge.org/docs/scripting/scripting.html

"""

import os
from pathlib import Path
import fontforge
import shutil
import math
from datetime import datetime
from ruamel.yaml import YAML
yaml = YAML()
yaml.sort_base_mapping_type_on_output = None
yaml.indent(mapping=2, sequence=4, offset=2)


class FontX():
    def __init__(self, config_file: os.PathLike = './ffxcfg.yml'):
        self.config_file = config_file
        self.working_dir = Path(self.config_file).parent
        with open(self.config_file, 'r', encoding='utf8') as yr:
            self.config = yaml.load(yr)

        self.new_name = self.config['NEW_FONT_NAME']
        self.target_dir = self.working_dir / self.new_name
        os.makedirs(self.target_dir, exist_ok=True)

        self.PRESET_HARD_CODED_UNDERLINE_THICKNESS = self.config['PRESET_HARD_CODED_UNDERLINE_THICKNESS']

        _src = self.config['SOURCE_FILE']
        self.source_file = self.working_dir / _src if not os.path.isabs(_src) else _src
        self.target_source_file = self.target_dir / (self.new_name + '.sfd')
        self.target_exported_file = self.target_dir / (self.new_name + '.ttf')
        shutil.copy(self.source_file, self.target_source_file)
        self.font = fontforge.open(os.path.abspath(self.target_source_file))

        self.modify()
        self.install()

    def modify(self):
        self.old_name = self.font.fontname
        self.font.fontname = self.new_name
        self.font.familyname = self.new_name
        self.font.fullname = self.new_name

        # calculations
        fixed_width = self.font['x'].width
        formal_ascent = self.font.ascent
        formal_em = self.font.em
        self.font.ascent = math.ceil(fixed_width * 2 / formal_em * formal_ascent)
        self.font.descent = fixed_width * 2 - self.font.ascent
        self.font.os2_winascent = self.font.ascent
        self.font.os2_windescent = self.font.descent
        self.font.os2_typoascent = self.font.ascent
        self.font.os2_typodescent = -1 * self.font.descent
        # os2 hhead ascent/descent
        self.font.hhea_ascent = self.font.ascent
        self.font.hhea_descent = -1 * self.font.descent
        # the underline position
        self.font.upos = -1 * (self.font.descent - self.PRESET_HARD_CODED_UNDERLINE_THICKNESS)

        self.font.comment = f'This font is the X version(EM W:H=1:2) of {self.old_name}'
        self.font.copyright = self.font.copyright + f'\n{self.font.comment}'
        self.font.save()
        self.font.generate(os.path.abspath(self.target_exported_file))

    def install(self):
        # mind that for now this install procedure is only for linux operation systems.
        os.chdir(self.target_source_file.parent)
        commands = [
            f'mv ~/.local/share/fonts/{self.new_name}.* ~/trash',
            f'cp {self.new_name}.*tf ~/.local/share/fonts/',
            'fc-cache -fv',
            f'echo \'{self.new_name} Generated via FontX, {datetime.now()}\' >> FontX.log'
        ]
        for cmd in commands:
            os.system(cmd)


if __name__ == "__main__":
    x = FontX()
