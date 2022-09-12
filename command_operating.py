from dataclasses import dataclass, asdict
from process_history import ShowQueryHistory
import process_hotels as ph
from logging_class import my_log


@dataclass(slots=True, frozen=True)
class Processes:
    """
    Dataclass which contains Classes which implement certain functionality
    """
    price: ph.Processor = ph.Processor
    history: ShowQueryHistory = ShowQueryHistory


@my_log
class CommandManager:
    """
    Class which resolutes one of commands
    """
    def __init__(self, params: str):
        if params in ['best_deal', 'lowest_price', 'highest_price']:
            params = 'price'
        self._pr_inst = Processes()
        self._process = asdict(self._pr_inst).get(params)

    async def resp_to_user(self, **kwargs):
        """
        Method which receives kwargs arguments, creates instance of process
        class and runs its func
        :param kwargs:
        :return:
        """
        s = self._process(**kwargs)
        await s.operate()
