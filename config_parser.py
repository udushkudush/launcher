import json
import os
import re
from os.path import dirname, join, normpath

os.environ['PIPELINE_ROOT'] = "C:/tools"


class ParseConfig:
    def __init__(self):
        self.config_dir = join(dirname(__file__), 'configs')
        self.env = dict()
        # self.current_config = None
        self.sys_env = os.environ.copy()
        self.main_config = self.load_main_config()

    @staticmethod
    def get_env(val):
        return re.findall(r"\%(\w+)\%", val)

    def parse_config(self, conf):
        """
        Собирает конфиг, вставляет инклюды и резолвит в нем все перменные в абсолютные пути
        :param conf:
        :return:
        """

        self.env = self.sys_env.copy()
        self.env.update(conf.copy())

        # сначала забираем инклюды
        include = self.env.get('include')  # проверяем есть ли инклюды
        for i in include:
            val = self.main_config.get(i)  # сначала поищем инклюд в основном конфиге
            if val:
                # если есть, тогда выполняем сл. код
                # print(val.items())
                for k, v in val.items():
                    if k.islower():
                        if k == 'comment':
                            continue
                    self.inject_env(k, v)
            else:
                # если нету, тогда выполняем ищем соответствующий файл и выполняем код
                val = self.get_file_config(i)
                for k, v in val.items():
                    self.inject_env(k, v)

        # после добавления инклюдов, их список можно удалить
        self.env.pop('include')

        # теперь пробегаемся дальше по входящему конфигу, надо резолвить перменные
        for k, v in self.env.items():
            # пропускаем если ключ строчными буквами или если значение не строка
            if k.islower():
                if not isinstance(v, str):
                    continue
                # пробуем резолвить перменные
                v = self.resolve_variable(v)
                # print(v)
            # остальное добавляем в переменную
            self.inject_env(k, v)

    def resolve_variable(self, var):
        # ищем по синтаксису перменную
        res = self.get_env(var)
        if res:
            # теперь найдем в цикле значение этих перменных
            for r in res:
                # сначала запрашиваем в системных перменных, затем в env класса,
                # если и там нет, тогда остается поиск в редактируемом конфиге
                env = os.getenv(r, self.env.get(r))
                if env:
                    # если найдено, заменяем синтакцическую перменную на ее значение
                    var = var.replace(f"%{r}%", env)

                    # и снова проверяем на наличие заменяем синтакцическую перменную на ее значение
                    check = self.get_env(var)
                    if check:
                        var = self.resolve_variable(var)
            return var
        return var

    def inject_env(self, env, val):
        """
        Функция обновляет значение в перменной
        :param env:
        :param val:
        :return:
        """
        # сначала попробуем получить значение переменной в основном конфиге
        _env = self.env.get(env, "")

        if isinstance(val, str) and val.startswith('|'):
            # если значение строка и начинается со знака |, тогда значение перменной оверайдим
            self.env[env] = val[1:]
            return
        val = str(val).split(os.pathsep)
        # print(val)
        if _env:
            # print(f'found: {_env}')
            # значение переменной найдено, значт добавляем к ним новое значение
            _env = [x.replace('\\', '/') for x in _env.split(os.pathsep) if x] + val
        else:
            # не найдено значение перменной
            _env = val

        # резолвим синтаксические перменные на их значения
        __ = []
        for _e in _env:
            __.append(self.resolve_variable(_e.replace('\\', '/')))

        # удаляем повторы, и собираем в строку
        _env = os.pathsep.join(sorted(list(set(__))))

        # втавляем обновленное значение перменной в наш основной конфиг
        self.env[env] = _env

    def get_file_config(self, config):
        """
        Функция загружает файл конфига, на вход имя конфиг файла
        :param config:
        :return:
        """
        print(f"loading config...")
        key = None
        if "|" in config:
            # в имени конфига есть разделитель, после него идет имя ключа который надо забрать
            config, key = config.split("|")

        with open(join(self.config_dir, config), 'r') as c:
            if key:
                __ = json.loads(c.read()).get(key)
                print(f"Key: {key}\n{json.dumps(__, indent=4, separators=(',', ':'))}")
                return __
            return json.loads(c.read())

    def load_main_config(self):
        with open(join(self.config_dir, 'main_config.json'), 'r') as config:
            return json.loads(config.read())


if __name__ == '__main__':

    MC = ParseConfig()
    m_cfg = MC.main_config['Maya2020']
    MC.parse_config(m_cfg)
    print(json.dumps(MC.env, indent=4, separators=(',', ':')))

