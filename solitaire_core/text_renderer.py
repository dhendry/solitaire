import itertools

from typing import List

from solitaire_core import game

WIDTH = 24 * 3
HEIGHT = 42


def _suit_symb(suit: game.Suit) -> str:
    if suit == game.CLUBS:
        return "♣"

    if suit == game.DIAMONDS:
        return "♦"

    if suit == game.HEARTS:
        return "♥"

    if suit == game.SPADES:
        return "♠"

    raise Exception(f"Unknown suit {suit}")


def _rank_symb(rank: game.CardRank) -> str:
    if 2 <= rank <= 10:
        return str(rank)

    if rank == game.ACE:
        return "A"

    if rank == game.JACK:
        return "J"

    if rank == game.QUEEN:
        return "Q"

    if rank == game.KING:
        return "K"

    raise Exception(f"Unknown rank {rank}")


def _add_color(txt: str, suit: game.Suit) -> str:
    if suit in game.RED_SUITS:
        return "\033[31m" + txt + "\033[0m"

    return txt


def _draw(screen, string, x, y):
    row = screen[y]
    for i, c in enumerate(string):
        row[x + i] = c


def _draw_card(screen, x: int, y: int, suit: game.Suit = None, rank: game.CardRank = None):
    """
    X and Y for top left corner
    """
    _draw(screen, "+-----+", x, y)
    for i in range(1, 4):
        screen[y + i][x] = "|"
        screen[y + i][x + 6] = "|"

    if rank:
        _draw(screen, _rank_symb(rank).ljust(2), x + 2, y + 1)

    if suit:
        _draw(screen, _suit_symb(suit), x + 4, y + 1)

    _draw(screen, "+-----+", x, y + 4)


def render(gs: game.VisibleGameState, actions: List[game.Action] = None) -> str:
    """
    Pretty fuckin hacky...
    """
    screen = [[" "] * WIDTH for _ in range(HEIGHT)]

    # Talon:
    talon_height_offset = 0
    for i, card in enumerate(reversed(game.bitmask_to_cards(gs.talon))):
        left_offset = WIDTH - 3 * (i + 1)
        _draw(screen, "+--", left_offset, talon_height_offset)
        _draw(screen, "|", left_offset, talon_height_offset + 1)
        _draw(screen, "|" + _rank_symb(card.rank), left_offset, talon_height_offset + 2)
        _draw(screen, "|" + _suit_symb(card.suit), left_offset, talon_height_offset + 3)
        _draw(screen, "|", left_offset, talon_height_offset + 4)
        _draw(screen, "+--", left_offset, talon_height_offset + 5)

    # Suit stacks:
    suit_height_offset = 7
    suit_left_offset = 1
    for i, suit in enumerate(game.Suit.values()[1:]):
        _draw_card(
            screen,
            suit_left_offset,
            suit_height_offset + i * 6,
            suit=suit,
            rank=game.card_idx_to_rank(game.highest_card_idx(gs.suit_stack & game.SUIT_MASK[suit])),
        )

    # Build stacks
    build_height_offset = talon_height_offset + 5 + 2
    for build_idx in range(7):
        build_left_offset = 1 + build_idx * 9 + 9

        _draw(screen, str(build_idx), build_left_offset + 3, build_height_offset - 1)

        stack_v_offset = build_height_offset

        for _ in range(gs.build_stacks_num_hidden[build_idx]):
            _draw(screen, "+-----+", build_left_offset, stack_v_offset)
            stack_v_offset += 1

        if not gs.build_stacks[build_idx]:
            continue

        for i, card in enumerate(reversed(game.bitmask_to_cards(gs.build_stacks[build_idx]))):
            _draw(screen, "+-----+", build_left_offset, stack_v_offset)
            stack_v_offset += 1
            _draw(
                screen,
                "| " + _rank_symb(card.rank).ljust(2) + _suit_symb(card.suit) + " |",
                build_left_offset,
                stack_v_offset,
            )
            stack_v_offset += 1
            for _ in range(2):
                _draw(screen, "|     |", build_left_offset, stack_v_offset)
                stack_v_offset += 1
            _draw(screen, "+-----+", build_left_offset, stack_v_offset)

            stack_v_offset -= 2

    # Overall boarders:
    screen.insert(0, ["-"] * WIDTH)
    for i, row in enumerate(screen):
        if i == 0:
            row.insert(0, "+")
            row.append("+")
        else:
            row.insert(0, "|")
            row.append("|")
    screen.append(["+"] + ["-"] * WIDTH + ["+"])

    # Sanity check basic screen layout:
    assert len(screen) == HEIGHT + 2
    assert all(len(row) == WIDTH + 2 for row in screen)
    assert all(all(len(px) == 1 for px in row) for row in screen)

    # Now attach on the set of valid actions
    additional_v_offset = 2
    if actions is not None:
        screen[0] += " " * (2 + 3) + "Actions"

        a_prev = None
        for i, a in enumerate(actions):

            # Basic setup
            txt = " "
            txt += str(i).rjust(2)
            txt += ": "
            txt += game.ActionType.Name(a.type).ljust(17)

            # Suit or src buiild stack
            if a.type in {game.TO_SS_S, game.TALON_S_TO_BS_N, game.SS_S_TO_BS_N}:
                txt += game.Suit.Name(a.suit).ljust(8)
            elif a.type == game.BS_N_TO_BS_N:
                txt += str(a.build_stack_src).ljust(8)
            else:
                # Not currently hit (?)
                txt += " " * 8

            txt += " " * 2

            # Dest build stack
            if a.type in {game.TALON_S_TO_BS_N, game.SS_S_TO_BS_N, game.BS_N_TO_BS_N}:
                txt += str(a.build_stack_dest).ljust(2)
            else:
                txt += " " * 2

            # Separation between types of actions - note: not checking bounds on offset (meh)
            if a_prev is not None and a_prev.type != a.type:
                additional_v_offset += 1
            a_prev = a

            screen[i + additional_v_offset].append(txt)

        screen[additional_v_offset + len(actions) + 1].append("  n: New game")
        screen[additional_v_offset + len(actions) + 2].append("  q: Quit")

    # Finally join it all together
    rendered = "\n".join("".join(s) for s in screen)
    # SUPER FUCKING HACKY: add red coloring:
    for s in game.RED_SUITS:
        rendered = rendered.replace(_suit_symb(s), _add_color(_suit_symb(s), s))
        rendered = rendered.replace(game.Suit.Name(s), _add_color(game.Suit.Name(s), s))

    return rendered
