"""Per-model circuit breaker; one half-open probe, no implicit retries."""
import asyncio
import time


class ModelCircuit:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.states = {}

    async def call(self, key, operation, threshold=3, cooldown=300):
        state = self.states.setdefault(key, {'failures': 0, 'until': 0, 'probing': False})
        probe = bool(state['until'])
        if probe and (self.clock() < state['until'] or state['probing']):
            raise RuntimeError('model_circuit_open')
        if probe:
            state['probing'] = True
        try:
            result = await operation()
        except asyncio.CancelledError:
            raise
        except Exception:
            state['failures'] += 1
            if state['failures'] >= threshold:
                state['until'] = self.clock() + cooldown
            raise
        else:
            state.update(failures=0, until=0)
            return result
        finally:
            if probe:
                state['probing'] = False
