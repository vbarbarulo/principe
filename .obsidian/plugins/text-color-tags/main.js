const { Plugin, PluginSettingTab, Setting } = require('obsidian');
const { ViewPlugin, Decoration, WidgetType } = require('@codemirror/view');
const { RangeSetBuilder } = require('@codemirror/state');

const NAMED_COLORS = {
    'red': '#e74c3c',
    'orange': '#e67e22',
    'yellow': '#f1c40f',
    'green': '#2ecc71',
    'blue': '#3498db',
    'purple': '#9b59b6',
    'pink': '#e91e8d',
    'cyan': '#00bcd4',
    'gray': '#95a5a6',
    'white': '#ecf0f1',
    'black': '#2c3e50'
};

const DEFAULT_SETTINGS = {
    recentColors: [],
    vaultSwatches: [
        '#e74c3c', '#e67e22', '#f1c40f', '#2ecc71',
        '#3498db', '#9b59b6', '#e91e8d', '#00bcd4'
    ]
};

// Matches: $colorname, $#hex, $#rrggbb, or just $ (for picker)
const COLOR_REGEX = /\$(#?[a-fA-F0-9]{3,6}|red|orange|yellow|green|blue|purple|pink|cyan|gray|white|black)?\s*([^\$\n]*?)(?=\s*\$(?:#?[a-fA-F0-9]{3,6}|red|orange|yellow|green|blue|purple|pink|cyan|gray|white|black)?\s|\n|$)/gi;

function parseColor(colorStr) {
    if (!colorStr) return null;
    const lower = colorStr.toLowerCase();
    if (NAMED_COLORS[lower]) return NAMED_COLORS[lower];
    if (colorStr.startsWith('#')) return colorStr;
    if (/^[a-fA-F0-9]{3,6}$/.test(colorStr)) return '#' + colorStr;
    return null;
}

function colorToHex(color) {
    if (!color) return '#888888';
    if (color.startsWith('#')) return color;
    return NAMED_COLORS[color.toLowerCase()] || '#888888';
}

class ColorSwatchWidget extends WidgetType {
    constructor(color, plugin, pos, view) {
        super();
        this.color = color;
        this.plugin = plugin;
        this.pos = pos;
        this.view = view;
    }

    toDOM() {
        const swatch = document.createElement('span');
        swatch.className = 'color-tag-swatch' + (this.color ? '' : ' no-color');
        if (this.color) {
            swatch.style.backgroundColor = this.color;
        }

        swatch.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.plugin.showColorPicker(swatch, this.pos, this.view);
        });

        return swatch;
    }

    eq(other) {
        return other.color === this.color && other.pos === this.pos;
    }

    ignoreEvent() {
        return false;
    }
}

module.exports = class ColorTagsPlugin extends Plugin {
    async onload() {
        await this.loadSettings();
        this.addSettingTab(new ColorTagsSettingTab(this.app, this));

        this.registerMarkdownPostProcessor((el, ctx) => {
            this.processElement(el);
        });

        this.registerEditorExtension([this.createEditorExtension()]);

        // Add context menu item
        this.registerEvent(
            this.app.workspace.on('editor-menu', (menu, editor, view) => {
                menu.addItem((item) => {
                    item
                        .setTitle('Text Color')
                        .setIcon('palette')
                        .onClick(() => {
                            this.showColorPickerForSelection(editor);
                        });
                });
            })
        );

        this.pickerEl = null;
    }

    showColorPickerForSelection(editor) {
        const selection = editor.getSelection();
        const cursor = editor.getCursor('from');
        
        // Get screen coordinates for picker placement
        const cursorOffset = editor.posToOffset(cursor);
        const cm = editor.cm;
        const coords = cm.coordsAtPos(cursorOffset);
        
        if (this.pickerEl) {
            this.pickerEl.remove();
            this.pickerEl = null;
        }

        const picker = document.createElement('div');
        picker.className = 'color-tag-picker';

        // Color input row
        const colorInputRow = document.createElement('div');
        colorInputRow.className = 'color-tag-picker-row';

        const colorInput = document.createElement('input');
        colorInput.type = 'color';
        colorInput.value = '#e74c3c';
        colorInput.className = 'color-tag-picker-color-input';

        const hexInput = document.createElement('input');
        hexInput.type = 'text';
        hexInput.value = colorInput.value;
        hexInput.placeholder = '#ffffff';
        hexInput.className = 'color-tag-picker-hex-input';

        colorInput.addEventListener('input', () => {
            hexInput.value = colorInput.value;
        });

        hexInput.addEventListener('input', () => {
            const val = hexInput.value.startsWith('#') ? hexInput.value : '#' + hexInput.value;
            if (/^#[a-fA-F0-9]{3}$|^#[a-fA-F0-9]{6}$/.test(val)) {
                colorInput.value = val.length === 4 
                    ? '#' + val[1] + val[1] + val[2] + val[2] + val[3] + val[3]
                    : val;
            }
        });

        colorInputRow.appendChild(colorInput);
        colorInputRow.appendChild(hexInput);
        picker.appendChild(colorInputRow);

        // Vault swatches
        const vaultLabel = document.createElement('div');
        vaultLabel.className = 'color-tag-picker-label';
        vaultLabel.textContent = 'Vault Colors';
        picker.appendChild(vaultLabel);

        const vaultRow = this.createSwatchRow(this.settings.vaultSwatches, (color) => {
            colorInput.value = color;
            hexInput.value = color;
        });
        picker.appendChild(vaultRow);

        // Recent colors
        if (this.settings.recentColors.length > 0) {
            const recentLabel = document.createElement('div');
            recentLabel.className = 'color-tag-picker-label recent';
            recentLabel.textContent = 'Recent';
            picker.appendChild(recentLabel);

            const recentRow = this.createSwatchRow(this.settings.recentColors, (color) => {
                colorInput.value = color;
                hexInput.value = color;
            });
            picker.appendChild(recentRow);
        }

        // Apply button
        const applyBtn = document.createElement('button');
        applyBtn.className = 'color-tag-picker-apply';
        applyBtn.textContent = 'Apply';
        applyBtn.addEventListener('click', () => {
            let newColor = hexInput.value;
            if (!newColor.startsWith('#')) newColor = '#' + newColor;
            
            const colorCode = newColor.replace('#', '');
            
            if (selection) {
                // Wrap selected text
                const newText = `$${colorCode} ${selection}`;
                editor.replaceSelection(newText);
            } else {
                // Insert at cursor
                const newText = `$${colorCode} `;
                editor.replaceRange(newText, cursor);
                // Move cursor to end of inserted text
                editor.setCursor({ line: cursor.line, ch: cursor.ch + newText.length });
            }
            
            this.addRecentColor(newColor);
            picker.remove();
            this.pickerEl = null;
            editor.focus();
        });
        picker.appendChild(applyBtn);

        // Position picker near cursor
        if (coords) {
            picker.style.left = Math.min(coords.left || 100, window.innerWidth - 260) + 'px';
            picker.style.top = ((coords.top || 100) + 20) + 'px';
        } else {
            picker.style.left = '100px';
            picker.style.top = '100px';
        }

        document.body.appendChild(picker);
        this.pickerEl = picker;

        // Close on outside click
        const closeHandler = (e) => {
            if (!picker.contains(e.target)) {
                picker.remove();
                this.pickerEl = null;
                document.removeEventListener('mousedown', closeHandler);
            }
        };
        setTimeout(() => document.addEventListener('mousedown', closeHandler), 10);
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }

    addRecentColor(color) {
        const hex = colorToHex(color).toLowerCase();
        this.settings.recentColors = this.settings.recentColors.filter(c => c.toLowerCase() !== hex);
        this.settings.recentColors.unshift(hex);
        if (this.settings.recentColors.length > 8) {
            this.settings.recentColors = this.settings.recentColors.slice(0, 8);
        }
        this.saveSettings();
    }

    showColorPicker(anchorEl, pos, view) {
        if (this.pickerEl) {
            this.pickerEl.remove();
            this.pickerEl = null;
        }

        const picker = document.createElement('div');
        picker.className = 'color-tag-picker';

        const currentColor = this.getColorAtPos(view, pos);

        // Color input row
        const colorInputRow = document.createElement('div');
        colorInputRow.className = 'color-tag-picker-row';

        const colorInput = document.createElement('input');
        colorInput.type = 'color';
        colorInput.value = colorToHex(currentColor);
        colorInput.className = 'color-tag-picker-color-input';

        const hexInput = document.createElement('input');
        hexInput.type = 'text';
        hexInput.value = colorInput.value;
        hexInput.placeholder = '#ffffff';
        hexInput.className = 'color-tag-picker-hex-input';

        colorInput.addEventListener('input', () => {
            hexInput.value = colorInput.value;
        });

        hexInput.addEventListener('input', () => {
            const val = hexInput.value.startsWith('#') ? hexInput.value : '#' + hexInput.value;
            if (/^#[a-fA-F0-9]{3}$|^#[a-fA-F0-9]{6}$/.test(val)) {
                colorInput.value = val.length === 4 
                    ? '#' + val[1] + val[1] + val[2] + val[2] + val[3] + val[3]
                    : val;
            }
        });

        colorInputRow.appendChild(colorInput);
        colorInputRow.appendChild(hexInput);
        picker.appendChild(colorInputRow);

        // Vault swatches
        const vaultLabel = document.createElement('div');
        vaultLabel.className = 'color-tag-picker-label';
        vaultLabel.textContent = 'Vault Colors';
        picker.appendChild(vaultLabel);

        const vaultRow = this.createSwatchRow(this.settings.vaultSwatches, (color) => {
            colorInput.value = color;
            hexInput.value = color;
        });
        picker.appendChild(vaultRow);

        // Recent colors
        if (this.settings.recentColors.length > 0) {
            const recentLabel = document.createElement('div');
            recentLabel.className = 'color-tag-picker-label recent';
            recentLabel.textContent = 'Recent';
            picker.appendChild(recentLabel);

            const recentRow = this.createSwatchRow(this.settings.recentColors, (color) => {
                colorInput.value = color;
                hexInput.value = color;
            });
            picker.appendChild(recentRow);
        }

        // Apply button
        const applyBtn = document.createElement('button');
        applyBtn.className = 'color-tag-picker-apply';
        applyBtn.textContent = 'Apply';
        applyBtn.addEventListener('click', () => {
            let newColor = hexInput.value;
            if (!newColor.startsWith('#')) newColor = '#' + newColor;
            this.applyColor(view, pos, newColor);
            this.addRecentColor(newColor);
            picker.remove();
            this.pickerEl = null;
        });
        picker.appendChild(applyBtn);

        // Position picker
        const rect = anchorEl.getBoundingClientRect();
        picker.style.left = Math.min(rect.left, window.innerWidth - 260) + 'px';
        picker.style.top = (rect.bottom + 5) + 'px';

        document.body.appendChild(picker);
        this.pickerEl = picker;

        // Close on outside click
        const closeHandler = (e) => {
            if (!picker.contains(e.target) && e.target !== anchorEl) {
                picker.remove();
                this.pickerEl = null;
                document.removeEventListener('mousedown', closeHandler);
            }
        };
        setTimeout(() => document.addEventListener('mousedown', closeHandler), 10);
    }

    createSwatchRow(colors, onClick) {
        const row = document.createElement('div');
        row.className = 'color-tag-picker-swatches';

        for (const color of colors) {
            const swatch = document.createElement('div');
            swatch.className = 'color-tag-picker-swatch';
            swatch.style.backgroundColor = color;
            swatch.title = color;
            swatch.addEventListener('click', () => onClick(color));
            row.appendChild(swatch);
        }

        return row;
    }

    getColorAtPos(view, pos) {
        const line = view.state.doc.lineAt(pos);
        const text = line.text;
        const offset = pos - line.from;

        COLOR_REGEX.lastIndex = 0;
        let match;
        while ((match = COLOR_REGEX.exec(text)) !== null) {
            if (match.index <= offset && match.index + match[0].length >= offset) {
                return parseColor(match[1]);
            }
        }
        return null;
    }

    applyColor(view, pos, newColor) {
        const line = view.state.doc.lineAt(pos);
        const text = line.text;
        const offset = pos - line.from;

        COLOR_REGEX.lastIndex = 0;
        let match;
        while ((match = COLOR_REGEX.exec(text)) !== null) {
            const matchStart = match.index;
            const matchEnd = match.index + match[0].length;

            if (matchStart <= offset && matchEnd >= offset) {
                const contentText = match[2] || '';
                const oldColorPart = match[1] || '';

                const docMatchStart = line.from + matchStart;
                const colorPartEnd = line.from + matchStart + 1 + oldColorPart.length;

                // Remove # prefix for cleaner syntax
                const newColorStr = newColor.replace('#', '');

                // Figure out what to replace
                let replaceFrom = docMatchStart;
                let replaceTo = colorPartEnd;

                // If there's a space after the color, keep it
                const hasSpaceAfter = text[matchStart + 1 + oldColorPart.length] === ' ';

                view.dispatch({
                    changes: { from: replaceFrom, to: replaceTo, insert: '$' + newColorStr }
                });

                return;
            }
        }
    }

    processElement(el) {
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        const nodesToProcess = [];

        while (walker.nextNode()) {
            nodesToProcess.push(walker.currentNode);
        }

        for (const node of nodesToProcess) {
            const text = node.textContent;
            COLOR_REGEX.lastIndex = 0;

            if (COLOR_REGEX.test(text)) {
                const fragment = document.createDocumentFragment();
                let lastIndex = 0;
                let match;

                COLOR_REGEX.lastIndex = 0;
                while ((match = COLOR_REGEX.exec(text)) !== null) {
                    if (match.index > lastIndex) {
                        fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
                    }

                    const color = parseColor(match[1]);
                    const content = match[2].trim();

                    if (color && content) {
                        const span = document.createElement('span');
                        span.style.color = color;
                        span.textContent = content;
                        fragment.appendChild(span);
                    } else if (content) {
                        fragment.appendChild(document.createTextNode(content));
                    }

                    lastIndex = match.index + match[0].length;
                }

                if (lastIndex < text.length) {
                    fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
                }

                node.parentNode.replaceChild(fragment, node);
            }
        }
    }

    createEditorExtension() {
        const plugin = this;

        return ViewPlugin.fromClass(class {
            constructor(view) {
                this.decorations = this.buildDecorations(view);
            }

            update(update) {
                if (update.docChanged || update.viewportChanged || update.selectionSet || update.focusChanged) {
                    this.decorations = this.buildDecorations(update.view);
                }
            }

            buildDecorations(view) {
                const builder = new RangeSetBuilder();
                const selection = view.state.selection.main;
                const decorations = [];

                for (const { from, to } of view.visibleRanges) {
                    const text = view.state.doc.sliceString(from, to);
                    let match;
                    const localRegex = /\$(#?[a-fA-F0-9]{3,6}|red|orange|yellow|green|blue|purple|pink|cyan|gray|white|black)?\s*([^\$\n]*?)(?=\s*\$(?:#?[a-fA-F0-9]{3,6}|red|orange|yellow|green|blue|purple|pink|cyan|gray|white|black)?\s|\n|$)/gi;

                    while ((match = localRegex.exec(text)) !== null) {
                        const matchStart = from + match.index;
                        const colorPart = match[1] || '';
                        const contentPart = match[2] || '';
                        const tagEnd = matchStart + 1 + colorPart.length;
                        const charAfterTag = text[match.index + 1 + colorPart.length];
                        const hasSpace = charAfterTag === ' ';
                        const textStart = tagEnd + (hasSpace ? 1 : 0);
                        const matchEnd = matchStart + match[0].length;
                        const color = parseColor(colorPart);

                        // Check if cursor is anywhere within this color tag region
                        const cursorInRange = selection.from >= matchStart && selection.from <= matchEnd;

                        if (cursorInRange) {
                            // Editing: show swatch + full tag text, all colored
                            decorations.push({
                                from: matchStart,
                                to: matchStart,
                                decoration: Decoration.widget({
                                    widget: new ColorSwatchWidget(color, plugin, matchStart, view),
                                    side: 0
                                })
                            });

                            if (color) {
                                decorations.push({
                                    from: matchStart,
                                    to: matchEnd,
                                    decoration: Decoration.mark({
                                        attributes: { style: `color: ${color}` }
                                    })
                                });
                            }
                        } else {
                            // Not editing: hide tag, show colored content only (no swatch)
                            // Hide $color part
                            decorations.push({
                                from: matchStart,
                                to: textStart,
                                decoration: Decoration.replace({})
                            });

                            // Color the content
                            if (color && textStart < matchEnd) {
                                decorations.push({
                                    from: textStart,
                                    to: matchEnd,
                                    decoration: Decoration.mark({
                                        attributes: { style: `color: ${color}` }
                                    })
                                });
                            }
                        }
                    }
                }

                // Sort by position for RangeSetBuilder
                decorations.sort((a, b) => a.from - b.from || a.to - b.to);

                for (const d of decorations) {
                    builder.add(d.from, d.to, d.decoration);
                }

                return builder.finish();
            }
        }, {
            decorations: v => v.decorations
        });
    }
};

class ColorTagsSettingTab extends PluginSettingTab {
    constructor(app, plugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display() {
        const { containerEl } = this;
        containerEl.empty();

        containerEl.createEl('h2', { text: 'Color Tags Settings' });

        // Vault swatches
        containerEl.createEl('h3', { text: 'Vault Swatches' });
        containerEl.createEl('p', {
            text: 'Define 8 quick-access colors for your vault. These appear in the color picker.',
            cls: 'setting-item-description'
        });

        const swatchContainer = containerEl.createDiv();
        swatchContainer.style.cssText = 'display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 16px 0; max-width: 400px;';

        for (let i = 0; i < 8; i++) {
            const swatchWrapper = swatchContainer.createDiv();
            swatchWrapper.style.cssText = 'display: flex; align-items: center; gap: 8px;';

            const colorInput = swatchWrapper.createEl('input');
            colorInput.type = 'color';
            colorInput.value = this.plugin.settings.vaultSwatches[i] || '#ffffff';
            colorInput.style.cssText = 'width: 36px; height: 28px; border: none; cursor: pointer; padding: 0;';

            const hexLabel = swatchWrapper.createEl('code');
            hexLabel.textContent = colorInput.value;
            hexLabel.style.cssText = 'font-size: 11px; color: var(--text-muted);';

            colorInput.addEventListener('change', async () => {
                this.plugin.settings.vaultSwatches[i] = colorInput.value;
                hexLabel.textContent = colorInput.value;
                await this.plugin.saveSettings();
            });
        }

        // Recent colors
        containerEl.createEl('h3', { text: 'Recent Colors' });

        if (this.plugin.settings.recentColors.length > 0) {
            const recentContainer = containerEl.createDiv();
            recentContainer.style.cssText = 'display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0;';

            for (const color of this.plugin.settings.recentColors) {
                const swatch = recentContainer.createDiv();
                swatch.style.cssText = `
                    width: 28px;
                    height: 28px;
                    background-color: ${color};
                    border: 1px solid var(--background-modifier-border);
                    border-radius: 4px;
                `;
                swatch.title = color;
            }

            new Setting(containerEl)
                .setName('Clear recent colors')
                .setDesc('Remove all colors from recent history')
                .addButton(btn => btn
                    .setButtonText('Clear')
                    .onClick(async () => {
                        this.plugin.settings.recentColors = [];
                        await this.plugin.saveSettings();
                        this.display();
                    }));
        } else {
            containerEl.createEl('p', {
                text: 'No recent colors yet. Colors will appear here as you use them.',
                cls: 'setting-item-description'
            });
        }

        // Usage guide
        containerEl.createEl('h3', { text: 'Usage' });
        const usage = containerEl.createEl('div');
        usage.style.cssText = 'background: var(--background-secondary); padding: 12px; border-radius: 6px; font-family: var(--font-monospace); font-size: 13px;';
        usage.innerHTML = `
            <div style="margin-bottom: 8px;"><strong>Named colors:</strong></div>
            <div style="margin-left: 12px; color: var(--text-muted);">$red This is red text</div>
            <div style="margin-left: 12px; color: var(--text-muted);">$blue Blue text here</div>
            <div style="margin: 12px 0 8px 0;"><strong>Hex colors:</strong></div>
            <div style="margin-left: 12px; color: var(--text-muted);">$fff White text</div>
            <div style="margin-left: 12px; color: var(--text-muted);">$#ff5500 Orange text</div>
            <div style="margin: 12px 0 8px 0;"><strong>Picker only:</strong></div>
            <div style="margin-left: 12px; color: var(--text-muted);">$ Click swatch to pick</div>
        `;
    }
}
/* nosourcemap */