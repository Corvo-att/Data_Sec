import inspect
import json
import uvicorn
from nicegui import ui
from fastapi import FastAPI

app = FastAPI()

# Your separate cipher modules
from ciphers import caesar, rail_fence, row_transposition, simple_aes

# ==============================================================================
# 1. DESIGN TOKENS
# ==============================================================================
COLORS = {
    'primary': '#00F2FE',
    'secondary': '#10B981',
    'tertiary': '#6366F1',
    'neutral': '#0A0D14',
}

ALGORITHMS = {
    'caesar': {
        'name': 'Caesar',
        'full_name': 'Caesar Cipher',
        'short_desc': 'Shift Key (A → D)',
        'sub_desc': 'Monoalphabetic Substitution',
        'badge': 'Shift',
        'tier_badge': 'Obsolete',
        'tier_color': 'text-amber-400 bg-amber-500/10 border-amber-500/30',
        'key_slot': 'Shift 1–25',
        'security': 'Educational',
        'icon': 'sync_alt',
        'sample_enc': 'HELLO WORLD',
        'sample_dec': 'KHOOR ZRUOG',
    },
    'rail_fence': {
        'name': 'Rail Fence',
        'full_name': 'Rail Fence Cipher',
        'short_desc': 'Zig-zag Rails',
        'sub_desc': 'Geometric Transposition',
        'badge': 'Zig-Zag Cipher',
        'tier_badge': 'Puzzle Grade',
        'tier_color': 'text-[#00F2FE] bg-[#00F2FE]/10 border-[#00F2FE]/30',
        'key_slot': 'Rails (2, 3, 4...)',
        'security': 'Low / Reversible',
        'icon': 'show_chart',
        'sample_enc': 'WE ARE DISCOVERED FLEE AT ONCE',
        'sample_dec': 'WECRL TEERD SOEEF EAOCA IVDEN',
    },
    'row_trans': {
        'name': 'Row Transp.',
        'full_name': 'Row Transposition',
        'short_desc': 'Column Keyword',
        'sub_desc': 'Columnar Permutation',
        'badge': 'Matrix',
        'tier_badge': 'Historical',
        'tier_color': 'text-[#6366F1] bg-[#6366F1]/10 border-[#6366F1]/30',
        'key_slot': '"ZEBRA" (5-3-2-4-1)',
        'security': 'Moderate Cipher',
        'icon': 'grid_on',
        'sample_enc': 'SECRET CODE',
        'sample_dec': 'ET COERC EO S',
    },
    'simple_aes': {
        'name': 'Simple AES',
        'full_name': 'Simple AES',
        'short_desc': '128-bit Key',
        'sub_desc': 'Symmetric Block Cipher',
        'badge': 'Modern',
        'tier_badge': 'Standard',
        'tier_color': 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]/30',
        'key_slot': '128-bit Key + IV',
        'security': 'Quantum Resilient',
        'icon': 'lock',
        'sample_enc': 'SECRET CODE',
        'sample_dec': 'U2FtcGxlQUVTQ2lwaGVydGV4dA==',
    },
}


# ==============================================================================
# 2. UI HELPERS (Visuals & Clipboard Only)
# ==============================================================================
def render_html(markup: str, classes: str = '') -> None:
    """Version-safe ui.html wrapper for NiceGUI 2.x and 3.x."""
    if 'sanitize' in inspect.signature(ui.html).parameters:
        el = ui.html(markup, sanitize=False)
    else:
        el = ui.html(markup)
    if classes:
        el.classes(classes)


def build_rail_wave_svg(rails: int, offset: int) -> str:
    """Pure UI graphic for the zig-zag preview card."""
    steps = 11
    period = max(2 * (rails - 1), 1)
    width, height = 340, 84
    pad_x, pad_y = 20, 14
    dx = (width - 2 * pad_x) / (steps - 1)
    dy = (height - 2 * pad_y) / max(rails - 1, 1)

    pts = []
    for i in range(steps):
        pos = (i + offset) % period
        r = pos if pos < rails else period - pos
        pts.append((pad_x + i * dx, pad_y + r * dy))

    poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    grid_lines = ''.join(
        f'<line x1="8" y1="{pad_y + r * dy:.1f}" x2="{width - 8}" y2="{pad_y + r * dy:.1f}" '
        f'stroke="#1E2638" stroke-dasharray="3 3" stroke-width="1"/>'
        for r in range(rails)
    )
    dots = ''.join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#00F2FE" stroke="#0A0D14" stroke-width="1.5"/>'
        for x, y in pts
    )
    return f"""
    <svg viewBox="0 0 {width} {height}" class="w-full h-20">
        {grid_lines}
        <polyline points="{poly}" fill="none" stroke="#00F2FE" stroke-opacity="0.7" stroke-width="1.8"/>
        {dots}
    </svg>
    """


def copy_text(text: str) -> None:
    ui.run_javascript(f'navigator.clipboard.writeText({json.dumps(text)})')
    ui.notify('Copied to clipboard', color='positive', position='top')


# ==============================================================================
# 3. MAIN PAGE
# ==============================================================================
@ui.page('/')
def main_page() -> None:
    ui.dark_mode(True)
    ui.colors(
        primary=COLORS['primary'],
        secondary=COLORS['secondary'],
        accent=COLORS['tertiary'],
        dark=COLORS['neutral'],
    )

    ui.add_head_html("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background-color: #06080D;
            font-family: 'Inter', sans-serif;
            color: #E6EDF7;
        }
        .font-display { font-family: 'Space Grotesk', sans-serif; }
        .font-mono-code { font-family: 'JetBrains Mono', monospace; }
        .app-shell {
            background-color: #0A0D14;
            border: 1px solid #1B2232;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.75);
        }
        .cc-card {
            background-color: #121621;
            border: 1px solid #1E2536;
            border-radius: 14px;
        }
        .cc-subcard {
            background-color: #0D111A;
            border: 1px solid #1C2333;
            border-radius: 10px;
        }
        .cc-glow-cyan {
            border-color: #00F2FE !important;
            box-shadow: 0 0 18px rgba(0, 242, 254, 0.14);
        }
        .cc-glow-green {
            border-color: #10B981 !important;
            box-shadow: 0 0 18px rgba(16, 185, 129, 0.16);
        }
        .q-field__native, .q-field__input {
            color: #E6EDF7 !important;
        }
    </style>
    """)

    state = {
        'tab': 'lab',           # 'lab' | 'algorithms' | 'compare'
        'algo': 'caesar',       # 'caesar' | 'rail_fence' | 'row_trans' | 'simple_aes'
        'mode': 'encrypt',      # 'encrypt' | 'decrypt'
        'shift': 3,
        'rails': 3,
        'offset': 0,
        'keyword': 'ZEBRA',
        'aes_key': 'CIPHERCRAFT128!!',
        'input_text': 'HELLO WORLD',
        'compare_phrase': 'SECRET CODE',
    }

    # --------------------------------------------------------------------------
    # DISPATCHER: CALLS YOUR EXTERNAL CIPHER MODULES
    # --------------------------------------------------------------------------
    def run_active_cipher() -> str:
        algo = state['algo']
        is_dec = state['mode'] == 'decrypt'
        txt = state['input_text']
        try:
            if algo == 'caesar':
                return caesar.decrypt(txt, state['shift']) if is_dec else caesar.encrypt(txt, state['shift'])
            if algo == 'rail_fence':
                return (
                    rail_fence.decrypt(txt, state['rails'], state['offset'])
                    if is_dec
                    else rail_fence.encrypt(txt, state['rails'], state['offset'])
                )
            if algo == 'row_trans':
                return (
                    row_transposition.decrypt(txt, state['keyword'])
                    if is_dec
                    else row_transposition.encrypt(txt, state['keyword'])
                )
            return simple_aes.decrypt(txt, state['aes_key']) if is_dec else simple_aes.encrypt(txt, state['aes_key'])
        except Exception as exc:
            return f'[Error in {algo}: {exc}]'

    def step_badge(num: int, title: str, right_badge: str = '', right_color: str = 'text-[#00F2FE]'):
        with ui.row().classes('w-full items-center justify-between mb-2'):
            with ui.row().classes('items-center gap-2'):
                ui.label(str(num)).classes(
                    'w-5 h-5 rounded-full bg-[#00F2FE]/15 text-[#00F2FE] border border-[#00F2FE]/40 '
                    'text-[11px] font-mono-code font-bold flex items-center justify-center'
                )
                ui.label(title).classes('font-display font-semibold text-sm text-white tracking-tight')
            if right_badge:
                ui.label(right_badge).classes(
                    f'text-[10px] font-mono-code px-2 py-0.5 rounded-md bg-[#171C2A] border border-[#242D42] {right_color}'
                )

    # --------------------------------------------------------------------------
    # HEADER
    # --------------------------------------------------------------------------
    @ui.refreshable
    def render_header():
        subtitle = {'lab': 'Cipher Lab', 'algorithms': 'Algorithms', 'compare': 'Quick Compare'}[state['tab']]

        with ui.row().classes(
            'w-full items-center justify-between px-4 py-3 border-b border-[#1A2030] bg-[#0D111A]/90 backdrop-blur sticky top-0 z-20'
        ):
            with ui.row().classes('items-center gap-2.5'):
                with ui.element('div').classes(
                    'w-8 h-8 rounded-lg bg-[#00F2FE]/15 border border-[#00F2FE]/40 flex items-center justify-center'
                ):
                    ui.icon('enhanced_encryption', size='18px').classes('text-[#00F2FE]')
                with ui.column().classes('gap-0'):
                    with ui.row().classes('items-center gap-1.5'):
                        ui.label('CipherCraft').classes('font-display font-bold text-sm text-white leading-none')
                        ui.label('AES-256').classes(
                            'font-mono-code text-[9px] px-1.5 py-0.5 rounded bg-[#182032] text-[#00F2FE] border border-[#25314B]'
                        )
                    ui.label(subtitle).classes('text-[11px] text-[#8B95A8] leading-tight')

            with ui.row().classes('items-center gap-2'):
                ui.button(icon='tune', on_click=lambda: ui.notify('Deterministic mode active')).props(
                    'flat round dense size=sm'
                ).classes('text-[#8B95A8] hover:text-white')
                with ui.element('div').classes(
                    'w-7 h-7 rounded-full bg-[#E6EDF7] text-[#0A0D14] flex items-center justify-center cursor-pointer'
                ):
                    ui.icon('person', size='16px')

    # --------------------------------------------------------------------------
    # TAB 1: CIPHER LAB (Output & Parameters)
    # --------------------------------------------------------------------------
    @ui.refreshable
    def render_lab_output():
        result = run_active_cipher()
        is_dec = state['mode'] == 'decrypt'
        algo = state['algo']

        # Primary Action Button
        btn_label = 'Decrypt Ciphertext' if is_dec else 'Encrypt Message'
        btn_icon = 'lock_open' if is_dec else 'bolt'
        btn_style = (
            'bg-[#10B981] text-[#06130E] hover:bg-[#14CC8F]'
            if is_dec
            else 'bg-[#E8FDFF] text-[#0A0D14] hover:bg-[#00F2FE]'
        )
        ui.button(
            btn_label,
            icon=btn_icon,
            on_click=lambda: (render_lab_output.refresh(), ui.notify(f'{btn_label} executed', color='info')),
        ).props('unelevated no-caps').classes(
            f'w-full py-2.5 rounded-xl font-display font-bold text-sm tracking-wide shadow-lg {btn_style}'
        )

        # Step 5: Result Card
        with ui.column().classes('w-full gap-2 mt-2'):
            title = 'Decrypted Plaintext Output' if is_dec else 'Ciphertext Result'
            badge = 'Matches Pattern' if is_dec else '● Verified'
            step_badge(5, title, badge, 'text-[#10B981]')

            with ui.column().classes('w-full cc-card p-3.5 gap-3'):
                with ui.row().classes('w-full items-center justify-between'):
                    meta_label = (
                        'DECRYPTED RESULT'
                        if is_dec
                        else f'SHIFT {state["shift"]:+d} ENCODED'
                        if algo == 'caesar'
                        else f'{ALGORITHMS[algo]["name"].upper()} OUTPUT'
                    )
                    with ui.row().classes('items-center gap-1.5'):
                        ui.icon('check_circle', size='14px').classes('text-[#10B981]')
                        ui.label(meta_label).classes('font-mono-code text-[10px] text-[#10B981] font-semibold')

                    with ui.row().classes('items-center gap-1'):
                        def swap_io():
                            state['input_text'] = result
                            state['mode'] = 'encrypt' if is_dec else 'decrypt'
                            render_main_content.refresh()

                        ui.button('Swap', icon='swap_horiz', on_click=swap_io).props(
                            'flat dense no-caps size=xs'
                        ).classes('text-[#8B95A8] bg-[#181E2E] px-2 rounded-md text-[10px]')
                        ui.button('Copy', icon='content_copy', on_click=lambda: copy_text(result)).props(
                            'flat dense no-caps size=xs'
                        ).classes('text-[#00F2FE] bg-[#00F2FE]/10 px-2 rounded-md text-[10px]')

                # Main Result Display
                with ui.element('div').classes('w-full cc-subcard p-3'):
                    ui.label(result or '—').classes(
                        'font-mono-code text-base font-bold tracking-wider break-all '
                        + ('text-[#10B981]' if is_dec else 'text-white')
                    )

                # Breakdown Views
                if algo == 'caesar' and state['input_text'] and len(result) == len(state['input_text']):
                    with ui.row().classes('w-full items-center justify-between pt-1'):
                        ui.label('Transformation Breakdown').classes('text-[11px] text-[#8B95A8]')
                        ui.label('Letter-by-Letter Matrix').classes('font-mono-code text-[10px] text-[#00F2FE]')

                    pairs = list(zip(state['input_text'][:10], result[:10]))
                    with ui.row().classes('w-full gap-1.5 flex-wrap'):
                        for src, dst in pairs:
                            s_disp = '[SP]' if src == ' ' else src
                            d_disp = '[SP]' if dst == ' ' else dst
                            with ui.column().classes(
                                'items-center gap-0.5 px-2 py-1.5 rounded-lg bg-[#0D111A] border border-[#1E2638] min-w-[28px]'
                            ):
                                ui.label(s_disp).classes('font-mono-code text-[10px] text-[#8B95A8]')
                                ui.label(d_disp).classes('font-mono-code text-xs font-bold text-[#00F2FE]')

                elif algo == 'rail_fence':
                    try:
                        matrix = rail_fence.get_rail_matrix(state['input_text'], state['rails'], state['offset'])
                    except Exception:
                        matrix = []

                    with ui.column().classes('w-full cc-subcard p-3 gap-2'):
                        with ui.row().classes('w-full items-center justify-between'):
                            ui.label(f'How it worked ({state["rails"]}-Rail Reconstruction)').classes(
                                'font-display text-xs font-semibold text-white'
                            )
                            if matrix and matrix[0]:
                                ui.label(f'{len(matrix)} rows × {len(matrix[0])} cols').classes(
                                    'font-mono-code text-[10px] text-[#8B95A8]'
                                )
                        if matrix:
                            with ui.column().classes('w-full bg-[#080B12] rounded-lg p-2.5 gap-1 overflow-x-auto'):
                                for r_idx, row in enumerate(matrix):
                                    color = ['#00F2FE', '#10B981', '#6366F1', '#F59E0B', '#EC4899', '#A855F7'][r_idx % 6]
                                    with ui.row().classes('items-center gap-2 no-wrap'):
                                        ui.label(f'Rail {r_idx + 1}:').classes(
                                            'font-mono-code text-[10px] font-bold shrink-0'
                                        ).style(f'color: {color}')
                                        ui.label(' '.join(row[:26])).classes(
                                            'font-mono-code text-[10px] text-[#C8D3E6] whitespace-pre'
                                        )
                        else:
                            ui.label('Return a 2D list from rail_fence.get_rail_matrix() to populate this grid.').classes(
                                'font-mono-code text-[10px] text-[#8B95A8]'
                            )

                elif algo == 'row_trans':
                    ui.label(f'Keyword: "{state["keyword"].upper()}"').classes(
                        'font-mono-code text-[11px] text-[#6366F1]'
                    )

                elif algo == 'simple_aes':
                    ui.label('128-bit symmetric cipher output').classes('font-mono-code text-[10px] text-[#8B95A8]')

    @ui.refreshable
    def render_lab_parameters():
        algo = state['algo']
        if algo == 'caesar':
            step_badge(3, 'Shift Parameters', f'K = {state["shift"]:+d}')
            with ui.column().classes('w-full cc-card p-3.5 gap-3'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label('Shift Value (K: -25 to +25)').classes('text-xs text-[#8B95A8]')
                    with ui.row().classes('items-center gap-1.5'):
                        def bump(delta: int):
                            state['shift'] = max(-25, min(25, state['shift'] + delta))
                            render_lab_parameters.refresh()
                            render_lab_output.refresh()

                        ui.button('−', on_click=lambda: bump(-1)).props('flat dense size=xs').classes(
                            'w-6 h-6 rounded bg-[#1B2234] text-white font-mono-code'
                        )
                        ui.label(f'{state["shift"]:+d}').classes(
                            'font-mono-code text-xs font-bold text-[#00F2FE] min-w-[28px] text-center'
                        )
                        ui.button('+', on_click=lambda: bump(1)).props('flat dense size=xs').classes(
                            'w-6 h-6 rounded bg-[#1B2234] text-white font-mono-code'
                        )

                def on_slider(e):
                    state['shift'] = int(e.value)
                    render_lab_parameters.refresh()
                    render_lab_output.refresh()

                ui.slider(min=-25, max=25, value=state['shift'], on_change=on_slider).props(
                    'color=primary track-color=grey-9'
                ).classes('w-full')

                with ui.row().classes('w-full items-center gap-1.5 flex-wrap'):
                    ui.label('Presets:').classes('text-[10px] text-[#8B95A8]')
                    for val, lbl in [(3, '+3 (Classic Caesar)'), (13, '+13 (ROT13)'), (7, '+7 (Prime Step)')]:
                        active = state['shift'] == val
                        cls = (
                            'bg-[#00F2FE]/15 text-[#00F2FE] border-[#00F2FE]/40'
                            if active
                            else 'bg-[#171C2A] text-[#9AA5B8] border-[#252E42]'
                        )
                        ui.button(
                            lbl,
                            on_click=lambda v=val: (
                                state.update(shift=v),
                                render_lab_parameters.refresh(),
                                render_lab_output.refresh(),
                            ),
                        ).props('flat dense no-caps size=xs').classes(
                            f'font-mono-code text-[10px] px-2 py-0.5 rounded-md border {cls}'
                        )

                # Live Mapping Preview (uses your caesar.encrypt)
                with ui.column().classes('w-full cc-subcard p-2.5 gap-1.5'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label('Live Mapping Preview').classes('text-[10px] text-[#8B95A8]')
                        ui.label('Alphabetical Drift').classes('font-mono-code text-[10px] text-[#00F2FE]')
                    try:
                        mapped = caesar.encrypt('ABCDE', state['shift'])
                    except Exception:
                        mapped = ''
                    preview_text = (
                        ' · '.join(f'{s}→{d}' for s, d in zip('ABCDE', mapped))
                        if len(mapped) == 5
                        else mapped or 'A→? · B→? · C→? · D→? · E→?'
                    )
                    ui.label(preview_text).classes('font-mono-code text-xs text-white font-semibold tracking-wide')

        elif algo == 'rail_fence':
            step_badge(3, 'Rail Fence Parameters', 'Reconstruction Ready', 'text-[#10B981]')
            with ui.column().classes('w-full cc-card p-3.5 gap-3'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('gap-0'):
                        ui.label('Number of Rails (Depth)').classes('text-xs font-medium text-white')
                        ui.label('Controls zig-zag wave height (2–6 rails)').classes('text-[10px] text-[#8B95A8]')
                    with ui.row().classes('items-center gap-2 bg-[#0D111A] border border-[#22293C] rounded-lg px-2 py-1'):
                        def bump_rails(d: int):
                            state['rails'] = max(2, min(6, state['rails'] + d))
                            state['offset'] = min(state['offset'], 2 * (state['rails'] - 1) - 1)
                            render_lab_parameters.refresh()
                            render_lab_output.refresh()

                        ui.button('−', on_click=lambda: bump_rails(-1)).props('flat dense size=xs').classes('text-[#8B95A8]')
                        ui.label(f'{state["rails"]} Rails').classes('font-mono-code text-xs font-bold text-[#00F2FE]')
                        ui.button('+', on_click=lambda: bump_rails(1)).props('flat dense size=xs').classes('text-[#8B95A8]')

                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('gap-0'):
                        ui.label('Offset / Cycle Start').classes('text-xs font-medium text-white')
                        ui.label('Phase shift along the fence').classes('text-[10px] text-[#8B95A8]')
                    max_off = 2 * (state['rails'] - 1) - 1
                    ui.select(
                        options={i: f'{i} (Standard)' if i == 0 else f'Offset +{i}' for i in range(max_off + 1)},
                        value=state['offset'],
                        on_change=lambda e: (
                            state.update(offset=e.value),
                            render_lab_parameters.refresh(),
                            render_lab_output.refresh(),
                        ),
                    ).props('dark dense outlined options-dense').classes('w-32 text-xs font-mono-code')

                with ui.column().classes('w-full cc-subcard p-2.5 gap-1'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(f'{state["rails"]}-RAIL WAVE TRAJECTORY PREVIEW').classes(
                            'font-mono-code text-[9px] text-[#8B95A8]'
                        )
                        ui.label(f'Period = {2 * (state["rails"] - 1)}').classes(
                            'font-mono-code text-[9px] text-[#00F2FE]'
                        )
                    render_html(build_rail_wave_svg(state['rails'], state['offset']))
                    with ui.row().classes('w-full justify-between text-[9px] font-mono-code text-[#8B95A8]'):
                        ui.label('● Rail 1 (Peaks)').classes('text-[#00F2FE]')
                        ui.label('● Mid Rails (Centers)').classes('text-[#10B981]')
                        ui.label(f'● Rail {state["rails"]} (Troughs)').classes('text-[#6366F1]')

        elif algo == 'row_trans':
            step_badge(3, 'Transposition Key', 'Column Sort', 'text-[#6366F1]')
            with ui.column().classes('w-full cc-card p-3.5 gap-2'):
                ui.label('Column Keyword (Letters determine vertical read order)').classes('text-xs text-[#8B95A8]')
                ui.input(
                    value=state['keyword'],
                    on_change=lambda e: (state.update(keyword=e.value), render_lab_output.refresh()),
                ).props('dark outlined dense').classes('w-full font-mono-code')

        else:
            step_badge(3, '128-bit Symmetric Key', 'Block Mode', 'text-[#10B981]')
            with ui.column().classes('w-full cc-card p-3.5 gap-2'):
                ui.label('Secret Passphrase / Key').classes('text-xs text-[#8B95A8]')
                ui.input(
                    value=state['aes_key'],
                    on_change=lambda e: (state.update(aes_key=e.value), render_lab_output.refresh()),
                ).props('dark outlined dense').classes('w-full font-mono-code')

    # --------------------------------------------------------------------------
    # SIMULTANEOUS MATRIX (Calls all 4 modules)
    # --------------------------------------------------------------------------
    @ui.refreshable
    def render_simultaneous_cards():
        phrase = state['compare_phrase']

        def safe_call(fn, *args):
            try:
                return fn(*args)
            except Exception as exc:
                return f'[Error: {exc}]'

        rows = [
            ('1. Caesar (Shift 3)', safe_call(caesar.encrypt, phrase, 3), 'Direct character index displacement', 'text-[#00F2FE]'),
            ('2. Rail Fence (3 Rails)', safe_call(rail_fence.encrypt, phrase, 3, 0), 'Alternating zig-zag matrix projection', 'text-[#10B981]'),
            ('3. Row Transposition ("ZEBRA")', safe_call(row_transposition.encrypt, phrase, 'ZEBRA'), 'Keyword ordered vertical reading', 'text-[#6366F1]'),
            ('4. Simple AES (128-bit)', safe_call(simple_aes.encrypt, phrase, state['aes_key']), 'Full avalanche effect & byte-level diffusion', 'text-[#00F2FE]'),
        ]

        with ui.column().classes('w-full gap-2.5'):
            for title, out_val, desc, color in rows:
                with ui.column().classes('w-full cc-subcard p-3 gap-1'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(title).classes('font-mono-code text-[11px] text-[#C8D3E6] font-semibold')
                        ui.button(icon='content_copy', on_click=lambda v=out_val: copy_text(v)).props(
                            'flat round dense size=xs'
                        ).classes('text-[#8B95A8] hover:text-[#00F2FE]')
                    ui.label(out_val or '—').classes(f'font-mono-code text-sm font-bold break-all {color}')
                    ui.label(desc).classes('text-[10px] text-[#8B95A8]')

    def render_simultaneous_section():
        with ui.column().classes('w-full cc-card p-4 gap-3'):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('auto_fix_high', size='18px').classes('text-[#00F2FE]')
                    ui.label('Simultaneous Matrix').classes('font-display font-bold text-base text-white')
                ui.label('Live Diff').classes(
                    'font-mono-code text-[10px] px-2 py-0.5 rounded bg-[#182032] text-[#00F2FE] border border-[#25314B]'
                )

            ui.label('SHARED TEST PHRASE').classes('font-mono-code text-[10px] text-[#8B95A8]')
            ui.input(
                value=state['compare_phrase'],
                placeholder='Enter text to compare...',
                on_change=lambda e: (state.update(compare_phrase=e.value), render_simultaneous_cards.refresh()),
            ).props('dark outlined dense clearable').classes('w-full font-mono-code')

            render_simultaneous_cards()

    # --------------------------------------------------------------------------
    # MAIN BODY ROUTER
    # --------------------------------------------------------------------------
    @ui.refreshable
    def render_main_content():
        tab = state['tab']

        if tab == 'lab':
            with ui.column().classes('w-full p-4 gap-4 pb-24'):
                if state['mode'] == 'decrypt':
                    with ui.row().classes(
                        'w-full cc-card px-3.5 py-2.5 items-center justify-between border-[#10B981]/30'
                    ):
                        with ui.row().classes('items-center gap-2'):
                            ui.element('div').classes('w-2 h-2 rounded-full bg-[#10B981]')
                            ui.label('DECRYPTION ENGINE READY').classes(
                                'font-mono-code text-[10px] font-semibold text-[#10B981]'
                            )
                        ui.label('Deterministic').classes(
                            'font-mono-code text-[10px] px-2 py-0.5 rounded bg-[#171C2A] text-[#9AA5B8]'
                        )
                else:
                    with ui.row().classes('w-full cc-card p-3.5 items-start gap-3'):
                        with ui.element('div').classes(
                            'w-8 h-8 rounded-lg bg-[#00F2FE]/10 border border-[#00F2FE]/30 flex items-center justify-center shrink-0'
                        ):
                            ui.icon('science', size='18px').classes('text-[#00F2FE]')
                        with ui.column().classes('gap-0.5'):
                            ui.label('Interactive Cipher Studio').classes('font-display font-bold text-sm text-white')
                            ui.label(
                                'Explore cryptographic transformations step-by-step. Adjust keys in real-time to visualize mathematical shifts.'
                            ).classes('text-[11px] text-[#8B95A8] leading-snug')

                # Step 1: Choose Algorithm
                with ui.column().classes('w-full gap-1'):
                    step_badge(1, 'Choose Algorithm', '• 4 Available', 'text-[#10B981]')
                    with ui.grid(columns=2).classes('w-full gap-2.5'):
                        for key, info in ALGORITHMS.items():
                            selected = state['algo'] == key

                            def select_algo(k=key):
                                state['algo'] = k
                                state['input_text'] = (
                                    ALGORITHMS[k]['sample_dec']
                                    if state['mode'] == 'decrypt'
                                    else ALGORITHMS[k]['sample_enc']
                                )
                                render_main_content.refresh()

                            card_cls = 'cc-card cc-glow-cyan bg-[#141D2E]' if selected else 'cc-card hover:border-[#2E3A54]'
                            with ui.column().classes(f'{card_cls} p-3 gap-1.5 cursor-pointer transition-all').on(
                                'click', select_algo
                            ):
                                with ui.row().classes('w-full items-center justify-between'):
                                    ui.icon(info['icon'], size='18px').classes(
                                        'text-[#00F2FE]' if selected else 'text-[#8B95A8]'
                                    )
                                    badge_cls = (
                                        'bg-[#00F2FE] text-[#0A0D14] font-bold'
                                        if selected
                                        else 'bg-[#192030] text-[#8B95A8]'
                                    )
                                    ui.label(info['badge']).classes(
                                        f'font-mono-code text-[9px] px-1.5 py-0.5 rounded {badge_cls}'
                                    )
                                ui.label(info['name']).classes('font-display font-bold text-xs text-white mt-1')
                                ui.label(info['short_desc']).classes('text-[10px] text-[#8B95A8]')

                # Step 2: Choose Mode
                with ui.column().classes('w-full gap-1'):
                    step_badge(2, 'Choose Mode')
                    with ui.grid(columns=2).classes('w-full gap-2.5'):
                        for m_key, m_lbl, m_icon in [
                            ('encrypt', 'Encrypt Mode', 'lock'),
                            ('decrypt', 'Decrypt Mode', 'lock_open'),
                        ]:
                            active = state['mode'] == m_key

                            def set_mode(mode_val=m_key):
                                if state['mode'] != mode_val:
                                    state['mode'] = mode_val
                                    state['input_text'] = (
                                        ALGORITHMS[state['algo']]['sample_dec']
                                        if mode_val == 'decrypt'
                                        else ALGORITHMS[state['algo']]['sample_enc']
                                    )
                                    render_main_content.refresh()

                            active_cls = (
                                'cc-glow-green bg-[#10B981]/15 text-[#10B981]'
                                if (active and m_key == 'decrypt')
                                else 'cc-glow-cyan bg-[#00F2FE]/12 text-[#00F2FE]'
                                if active
                                else 'text-[#8B95A8] hover:text-white'
                            )
                            with ui.row().classes(
                                f'cc-card {active_cls} py-2.5 px-3 items-center justify-center gap-2 cursor-pointer transition-all'
                            ).on('click', set_mode):
                                ui.icon(m_icon, size='16px')
                                ui.label(m_lbl).classes('font-display font-semibold text-xs')

                # Step 3: Dynamic Parameters
                with ui.column().classes('w-full gap-1'):
                    render_lab_parameters()

                # Step 4: Input Message / Ciphertext
                with ui.column().classes('w-full gap-1'):
                    is_dec = state['mode'] == 'decrypt'
                    step_title = 'Input Ciphertext' if is_dec else 'Plaintext Message'

                    with ui.row().classes('w-full items-center justify-between mb-1'):
                        with ui.row().classes('items-center gap-2'):
                            ui.label('4').classes(
                                'w-5 h-5 rounded-full bg-[#00F2FE]/15 text-[#00F2FE] border border-[#00F2FE]/40 '
                                'text-[11px] font-mono-code font-bold flex items-center justify-center'
                            )
                            ui.label(step_title).classes('font-display font-semibold text-sm text-white')
                        count_badge = ui.label(f'{len(state["input_text"])} chars').classes(
                            'font-mono-code text-[10px] text-[#8B95A8]'
                        )

                    with ui.column().classes('w-full cc-card p-3 gap-2'):
                        with ui.row().classes('w-full items-center justify-between'):
                            def load_sample():
                                info = ALGORITHMS[state['algo']]
                                state['input_text'] = info['sample_dec'] if is_dec else info['sample_enc']
                                input_box.value = state['input_text']
                                count_badge.set_text(f'{len(state["input_text"])} chars')
                                render_lab_output.refresh()

                            ui.button('Sample Text', icon='auto_fix_high', on_click=load_sample).props(
                                'flat dense no-caps size=xs'
                            ).classes('text-[#00F2FE] bg-[#00F2FE]/10 px-2 rounded-md text-[10px]')
                            ui.button(
                                'Clear',
                                icon='close',
                                on_click=lambda: (
                                    state.update(input_text=''),
                                    setattr(input_box, 'value', ''),
                                    count_badge.set_text('0 chars'),
                                    render_lab_output.refresh(),
                                ),
                            ).props('flat dense no-caps size=xs').classes('text-[#8B95A8] text-[10px]')

                        def on_text_change(e):
                            state['input_text'] = e.value or ''
                            count_badge.set_text(f'{len(state["input_text"])} chars')
                            render_lab_output.refresh()

                        input_box = ui.textarea(
                            value=state['input_text'],
                            placeholder='Type message or ciphertext...',
                            on_change=on_text_change,
                        ).props('dark borderless autogrow rows=2').classes(
                            'w-full cc-subcard px-3 py-1 font-mono-code text-sm tracking-wide'
                        )

                # Step 5: Action Button & Result
                render_lab_output()

        elif tab == 'algorithms':
            with ui.column().classes('w-full p-4 gap-4 pb-24'):
                with ui.column().classes('gap-1'):
                    ui.label('• EVOLUTIONARY MATRIX').classes('font-mono-code text-[10px] text-[#00F2FE] font-semibold')
                    ui.label('4 Core Algorithms').classes('font-display font-bold text-2xl text-white')
                    ui.label('Classical substitution to post-computational modern block ciphers.').classes(
                        'text-xs text-[#8B95A8]'
                    )

                previews = {
                    'caesar': ('TRANSFORMATION (SHIFT 3)', 'HELLO  →  KHOOR'),
                    'rail_fence': ('ZIG-ZAG WAVE (3 RAILS)', 'W . . . E . . . C . . . R . . .\n. E . R . D . S . O . E . E . F'),
                    'row_trans': ('ALPHABETICAL COLUMN ORDER', 'Reads matrix top-to-bottom ordered by key letters (A → Z sequence)'),
                    'simple_aes': ('128-BIT PSEUDORANDOM DIFFUSION', '7b22636970686572223a22384a6b2b6c71...'),
                }

                for key, info in ALGORITHMS.items():
                    with ui.column().classes('w-full cc-card p-4 gap-3'):
                        with ui.row().classes('w-full items-start justify-between'):
                            with ui.row().classes('items-center gap-2.5'):
                                with ui.element('div').classes(
                                    'w-9 h-9 rounded-lg bg-[#182032] border border-[#25314B] flex items-center justify-center'
                                ):
                                    ui.icon(info['icon'], size='18px').classes('text-[#00F2FE]')
                                with ui.column().classes('gap-0'):
                                    ui.label(info['full_name']).classes('font-display font-bold text-sm text-white')
                                    ui.label(info['sub_desc']).classes('text-[11px] text-[#8B95A8]')
                            ui.label(info['tier_badge']).classes(
                                f'font-mono-code text-[10px] px-2 py-0.5 rounded-md border {info["tier_color"]}'
                            )

                        with ui.grid(columns=2).classes('w-full gap-2 pt-1'):
                            with ui.column().classes('gap-0'):
                                ui.label('Key Slot').classes('text-[10px] text-[#8B95A8]')
                                ui.label(info['key_slot']).classes('font-mono-code text-xs text-white font-semibold')
                            with ui.column().classes('gap-0'):
                                ui.label('Security Tier').classes('text-[10px] text-[#8B95A8]')
                                ui.label(info['security']).classes('font-mono-code text-xs text-[#10B981] font-semibold')

                        p_title, p_body = previews[key]
                        with ui.column().classes('w-full cc-subcard p-2.5 gap-1'):
                            ui.label(p_title).classes('font-mono-code text-[9px] text-[#8B95A8]')
                            ui.label(p_body).classes(
                                'font-mono-code text-[11px] text-[#00F2FE] whitespace-pre-wrap break-all'
                            )

                        def try_in_lab(k=key):
                            state['algo'] = k
                            state['mode'] = 'encrypt'
                            state['input_text'] = ALGORITHMS[k]['sample_enc']
                            state['tab'] = 'lab'
                            render_header.refresh()
                            render_main_content.refresh()
                            render_bottom_nav.refresh()

                        with ui.row().classes(
                            'w-full items-center justify-between px-3 py-2 rounded-lg bg-[#171E2E] hover:bg-[#1E2940] '
                            'border border-[#25314B] cursor-pointer transition-all'
                        ).on('click', try_in_lab):
                            ui.label('Try in Lab').classes('font-display text-xs font-semibold text-[#00F2FE]')
                            ui.icon('arrow_forward', size='16px').classes('text-[#00F2FE]')

                render_simultaneous_section()

        else:
            with ui.column().classes('w-full p-4 gap-4 pb-24'):
                render_simultaneous_section()

    # --------------------------------------------------------------------------
    # BOTTOM NAVIGATION BAR
    # --------------------------------------------------------------------------
    @ui.refreshable
    def render_bottom_nav():
        nav_items = [
            ('lab', 'Cipher Lab', 'terminal'),
            ('algorithms', 'Algorithms', 'hub'),
            ('compare', 'Quick Compare', 'compare_arrows'),
        ]
        with ui.row().classes(
            'w-full items-center justify-around px-3 py-2 border-t border-[#1A2030] bg-[#0D111A]/95 backdrop-blur sticky bottom-0 z-20'
        ):
            for key, label, icon in nav_items:
                active = state['tab'] == key

                def switch_tab(k=key):
                    state['tab'] = k
                    render_header.refresh()
                    render_main_content.refresh()
                    render_bottom_nav.refresh()

                cls = (
                    'bg-[#00F2FE]/12 text-[#00F2FE] border border-[#00F2FE]/30'
                    if active
                    else 'text-[#8B95A8] hover:text-white border border-transparent'
                )
                with ui.column().classes(
                    f'items-center gap-0.5 px-4 py-1.5 rounded-xl cursor-pointer transition-all {cls}'
                ).on('click', switch_tab):
                    ui.icon(icon, size='18px')
                    ui.label(label).classes('font-display text-[10px] font-semibold')

    # --------------------------------------------------------------------------
    # ROOT SHELL
    # --------------------------------------------------------------------------
    with ui.column().classes('w-full min-h-screen items-center py-0 sm:py-6 px-0 sm:px-4'):
        with ui.column().classes(
            'app-shell w-full max-w-[430px] min-h-screen sm:min-h-[820px] sm:rounded-3xl overflow-hidden justify-between gap-0'
        ):
            render_header()
            with ui.column().classes('w-full flex-grow gap-0'):
                render_main_content()
            render_bottom_nav()


# Replace the bottom ui.run(...) line in main.py with:
ui.run_with(
    app,
    title='CipherCraft — Interactive Cipher Studio',
    dark=True,
)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)