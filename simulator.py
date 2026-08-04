"""
Симуляция баннера персонажей Genshin Impact (Monte Carlo).

Механика (публично известна из официальных источников):
- Базовый шанс 5* — 0.6% за розыгрыш
- "Мягкая гарантия": с 74-го розыгрыша шанс растёт линейно
- "Жёсткая гарантия": на 90-м розыгрыше 5* выпадает гарантированно
- Правило 50/50: первый 5* на баннере — 50% шанс, что это баннерный
  персонаж, иначе — стандартный, но следующий 5* гарантированно баннерный
"""

import numpy as np

BASE_RATE = 0.006
SOFT_PITY_START = 74
HARD_PITY = 90
RATE_INCREASE_PER_PULL = 0.06
PRIMOGEMS_PER_PULL = 160


def pull_probability(pity: int) -> float:
    """Вероятность получить 5* на розыгрыше номер (pity + 1)."""
    if pity + 1 >= HARD_PITY:
        return 1.0
    if pity + 1 >= SOFT_PITY_START:
        steps_into_soft_pity = pity + 1 - SOFT_PITY_START + 1
        return min(1.0, BASE_RATE + steps_into_soft_pity * RATE_INCREASE_PER_PULL)
    return BASE_RATE


def simulate_until_copies(target_copies: int, start_pity: int = 0, start_guaranteed: bool = False, rng=None) -> int:
    """
    Крутит баннер, пока не наберёт target_copies баннерного персонажа.
    Возвращает число потраченных розыгрышей.
    """
    if rng is None:
        rng = np.random.default_rng()

    pulls = 0
    pity = start_pity
    guaranteed = start_guaranteed
    copies_obtained = 0

    while copies_obtained < target_copies:
        pulls += 1
        pity += 1

        if rng.random() < pull_probability(pity - 1):
            pity = 0
            if guaranteed or rng.random() < 0.5:
                copies_obtained += 1
                guaranteed = False
            else:
                guaranteed = True

    return pulls


def run_monte_carlo(target_copies: int, start_pity: int, start_guaranteed: bool, n_simulations: int = 20000):
    """Прогоняет симуляцию много раз, возвращает массив числа розыгрышей."""
    rng = np.random.default_rng(42)
    results = np.array([
        simulate_until_copies(target_copies, start_pity, start_guaranteed, rng)
        for _ in range(n_simulations)
    ])
    return results


def pulls_to_primogems(pulls: int) -> int:
    return pulls * PRIMOGEMS_PER_PULL
