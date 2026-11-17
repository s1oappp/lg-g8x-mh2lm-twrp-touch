# LG G8X `mh2lm`: техническое восстановление TWRP с сенсорным вводом

**Редакция:** 18 ноября 2026 г.

**Назначение:** передача другому AI/инженеру как проверенной инструкции по
идентификации, точному восстановлению, безопасной проверке и дальнейшей
диагностике TWRP для LG G8X ThinQ (`LMG850EMW`, platform/device codename
`mh2lm`).

## 1. Краткий итог

Проверенная рабочая комбинация на устройстве:

| Компонент | Рабочее значение |
|---|---|
| Текущий recovery boot image | TWRP 3.7.1_12-0, файл `files/twrp-mh2lm-3.7.1-ramtest-candidate.img` |
| SHA-256 образа | `b31b0cd4b8ec417bedefec020d5f2216295ba4d9ae67ed9296f43beece6305d3` |
| Постоянный boot target | `boot_b` |
| Активный слот при последней проверке | `b` |
| Kernel в работающем Recovery | `4.14.340-openela-perf+` |
| DTBO | исходный `dtbo_b`, не изменялся |
| Командная строка загрузчика | при последней проверке содержала `androidboot.dtbo_idx=5` |
| Сенсор | зарегистрирован как `touch_dev`; пользователь подтвердил работу после обычной перезагрузки 17 ноября 2026 г. в 23:57 (+03) |

Рабочим является **сочетание** recovery-образа и конфигурации B/DTBO B, а не
доказанное изменение драйвера внутри образа. Тот же образ при тесте с активным
слотом A (`dtbo_idx=3`) не регистрировал `touch_dev`; при B (`dtbo_idx=5`)
появился `touch_dev`, и во время отдельного RAM-теста были сохранены реальные
`BTN_TOUCH` и мультитач-события.

Файл-кандидат и `files/modded-twrp-g8x.img` — побайтно идентичны. Даже если
потерять файл-кандидат, его можно **точно** пересобрать из
`files/twrp-normal-mode.img`, который содержит те же kernel и ramdisk, но
дополнительно имеет аргумент `androidboot.mode=normal` и изменённый ID
загрузочного образа. Проверенный ниже Python-рецепт удаляет только этот
добавленный аргумент, заново вычисляет Android boot image ID и выдаёт файл,
побайтно совпадающий с рабочим кандидатом.

Полный исходный репозиторий/манифест, точный commit kernel/TWRP и первоначальная
команда получения `files/modded-twrp-g8x.img` не сохранены. Поэтому точная
восстановительная процедура из оставшегося бинарного донора воспроизводима;
полная независимая компиляция тех же kernel и ramdisk из исходников — нет,
если файлы-доноры также потеряны. Не выдавать неподтверждённую сборку за ту же
проверенную.

## 2. Статус и уровень доказательности

Разделяет **наблюдения** и **объяснения**:

1. **Подтверждённая загрузка:** кандидат загружался в TWRP 3.7.1_12-0; ADB
   переходил в состояние `recovery`.
2. **Подтверждённое обнаружение устройства:** `getevent -lp` и
   `/proc/bus/input/devices` показывали `touch_dev`, multitouch axes и
   `INPUT_PROP_DIRECT`. Одного этого недостаточно, чтобы утверждать, что
   реальные касания поступают.
3. **Сохранённые реальные события:** при RAM-загрузке кандидата с конфигурацией
   B трасса `files/touchfix-slotb-getevent.txt` содержит 2 `BTN_TOUCH DOWN`,
   2 `BTN_TOUCH UP`, 92 `ABS_MT_POSITION_X` и 59 `ABS_MT_POSITION_Y`.
4. **Работа после постоянной установки и перезагрузки:** пользователь
   подтвердил 17 ноября 2026 г. в 23:57 (+03), что после обычной перезагрузки
   сенсор работает в TWRP на слоте B.
   Независимый 30-секундный capture, сделанный ранее сразу после постоянной
   установки, пустой; он не является журналом касаний после этой более поздней
   перезагрузки.
5. **Дифференциальное наблюдение:** с тем же образом на A (`dtbo_idx=3`)
   `touch_dev` отсутствовал; при B (`dtbo_idx=5`) input и события присутствовали.
   Это экспериментально выделяет рабочую конфигурацию B. Это не доказывает
   первопричину и не доказывает, что вторая конфигурация неисправна только из-за
   DTBO: другие slot-зависимые различия бинарных разделов также требуют учёта.

### Не установлено

- Точный исходный проект/commit, из которого получены kernel и ramdisk внутри
  кандидата.
- Полное соответствие исходников kernel 4.14.223-perf+ конкретному бинарному
  TWRP 3.6.0, ранее не работавшему с сенсором.
- Внутренняя причина, почему тач не регистрировался с тем же кандидатом при
  `dtbo_idx=3`, но работал при `dtbo_idx=5`.
- Независимая запись `getevent` во время последнего подтверждения пользователя
  после обычной перезагрузки.

Не утверждать, что исправлением были правка DT, замена драйвера, подмена
`bootreasoncode` или установка `androidboot.mode=normal`. Эти утверждения не
подтверждены. В частности, экспериментальная правка DT ранее не привела к
рабочему ADB-сеансу Recovery.

## 3. Проверенные файлы и контрольные суммы

### 3.1. Образы и вход для точного восстановления

| Путь | Размер | SHA-256 | Назначение |
|---|---:|---|---|
| `files/twrp-mh2lm-3.7.1-ramtest-candidate.img` | 47 796 224 | `b31b0cd4b8ec417bedefec020d5f2216295ba4d9ae67ed9296f43beece6305d3` | Идентифицированный рабочий образ; этот файл был записан в `boot_b` |
| `files/modded-twrp-g8x.img` | 47 796 224 | `b31b0cd4b8ec417bedefec020d5f2216295ba4d9ae67ed9296f43beece6305d3` | Побайтно точная вторая копия кандидата |
| `files/twrp-normal-mode.img` | 47 796 224 | `ffc0a4e401192b57b00ba3bf90b23d8c17f675ae4fbad779ce8590b4d972c3bc` | Точный donor kernel+ramdisk; отличается cmdline и boot ID |

Перед использованием проверить хеши, а не доверять одному имени файла:

```sh
sha256sum \
  files/twrp-mh2lm-3.7.1-ramtest-candidate.img \
  files/modded-twrp-g8x.img \
  files/twrp-normal-mode.img
cmp files/twrp-mh2lm-3.7.1-ramtest-candidate.img files/modded-twrp-g8x.img
```

Для двух файлов-копий ожидается одинаковый SHA-256 и успешный `cmp`.

### 3.2. Android boot image header кандидата

Образ распознан как Android boot image с header version 0. Проверенные поля:

| Поле | Значение |
|---|---:|
| Magic | `ANDROID!` |
| Header version | `0` |
| Page size | `4096` |
| Kernel size | `20 070 008` байт |
| Kernel load address | `0x00008000` |
| Ramdisk size | `27 717 978` байт |
| Ramdisk load address | `0x01000000` |
| Second stage size | `0` |
| Tags address | `0x00000100` |
| Полный файл | `47 796 224` байта |
| Boot image ID | `a4606c945d527e2d9c34fd37a40fcfd30e4879b3` |

Ключевые параметры встроенной cmdline (это не всё содержимое строки):

```text
disable_skip_initramfs
androidboot.fastboot=1
androidboot.hardware=qcom
twrpfastboot=1
buildvariant=eng
```

`androidboot.mode=normal` **не входит** в cmdline проверенного кандидата. Его
содержит donor `twrp-normal-mode.img`; при восстановлении кандидата этот токен
удаляется.

### 3.3. Pre-write baseline разделов устройства

До постоянных изменений были сохранены полные копии:

| Baseline | Размер | SHA-256 |
|---|---:|---|
| `files/boot_a-readonly-baseline-20261117.img` | 100 663 296 | `47a1e55c1eafacc7e912ad72b02fe906f40912c19d79aafef524cb3c2b22439f` |
| `files/boot_b-readonly-baseline-20261117.img` | 100 663 296 | `bd42b7f4f80d51f0d79973559b5e654ed302b58ef3b8f4c65d6dad032a29f2bf` |
| `files/dtbo_a-readonly-baseline-20261117.img` | 25 165 824 | `13a73e66818127f9e1c53579fad3ab66984ed16214a1aca79e6090486637e397` |
| `files/dtbo_b-readonly-baseline-20261117.img` | 25 165 824 | `c1cb0641d82bc9fb738f5392b245b292e18b1ee4737d591cf7d59e69d01820f3` |

После теста `boot_a` восстановили из его baseline; полный readback совпал с
SHA-256 выше. Первые 47 796 224 байта `boot_b` побайтно совпали с кандидатом;
полный SHA-256 всего post-write-раздела `boot_b` не вычислялся. Полный readback
`dtbo_b` совпал со своим baseline. `dtbo_a`/`dtbo_b` не прошивались.

### 3.4. Трасса тач-событий

`files/touchfix-slotb-getevent.txt`:

- размер: 38 909 байт;
- SHA-256: `322f77e98e88c67b8d36598ee285bd67bf641fbe8c39557d498dfe075025cc61`;
- 2 `BTN_TOUCH DOWN`;
- 2 `BTN_TOUCH UP`;
- 92 `ABS_MT_POSITION_X`;
- 59 `ABS_MT_POSITION_Y`.

Трасса относится к RAM-тесту образа при активном слоте B и `dtbo_idx=5`.
Номер `/dev/input/eventN` динамический: в сохранённой трассе/input-check был
`event2`, а в поздней проверке установленного Recovery — `event3`. Не
зашивать номер event в инструкции; каждый раз находить его по имени `touch_dev`.

`files/touchfix-persistent-getevent.txt` имеет размер 0: capture после
постоянной установки был пустым. Это ограничение артефакта, а не отмена более
позднего прямого сообщения пользователя, что после перезагрузки touch работает.

## 4. Точное восстановление кандидата из donor-образа

### Предпосылки

Этот раздел восстанавливает **те же байты**, а не выполняет новую сборку Android.
Проверено, что:

- donor `files/twrp-normal-mode.img` и кандидат имеют одинаковые kernel и
  ramdisk побайтно;
- оба имеют page size 4096 и header version 0;
- donor отличается от кандидата cmdline-токеном `androidboot.mode=normal` и
  соответствующим полем boot image ID;
- удаление токена и пересчёт ID даёт файл длиной 47 796 224 байта, который
  совпадает с кандидатом **побайтно** (0 несовпадающих байтов);
- повторная проверка восстановленного файла дала ожидаемый SHA-256 кандидата.

### Команда восстановления

Запускать из корня проекта, где есть `files/twrp-normal-mode.img`. Скрипт
создаёт **новый** файл `files/twrp-mh2lm-3.7.1-rebuilt.img` в exclusive mode:
если такой путь уже существует, скрипт откажется его перезаписывать.
Оригинальные donor и candidate файлы не меняются.

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib
import struct

src = Path("files/twrp-normal-mode.img")
dst = Path("files/twrp-mh2lm-3.7.1-rebuilt.img")
expected_source_sha256 = (
    "ffc0a4e401192b57b00ba3bf90b23d8c17f675ae4fbad779ce8590b4d972c3bc"
)
expected_output_sha256 = (
    "b31b0cd4b8ec417bedefec020d5f2216295ba4d9ae67ed9296f43beece6305d3"
)
expected_output_size = 47_796_224

image = bytearray(src.read_bytes())
assert hashlib.sha256(image).hexdigest() == expected_source_sha256
assert image[:8] == b"ANDROID!"

(
    kernel_size,
    kernel_addr,
    ramdisk_size,
    ramdisk_addr,
    second_size,
    second_addr,
    tags_addr,
    page_size,
    header_version,
    os_version,
) = struct.unpack_from("<10I", image, 8)

assert header_version == 0
assert page_size == 4096
assert second_size == 0

cmdline = bytes(image[64:576]).split(b"\0", 1)[0]
suffix = b" androidboot.mode=normal"
assert cmdline.endswith(suffix)
new_cmdline = cmdline[:-len(suffix)]
assert b"disable_skip_initramfs" in new_cmdline
assert b"androidboot.mode=normal" not in new_cmdline
assert len(new_cmdline) <= 512
image[64:576] = new_cmdline + b"\0" * (512 - len(new_cmdline))

def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment

kernel_offset = page_size
ramdisk_offset = kernel_offset + align_up(kernel_size, page_size)
second_offset = ramdisk_offset + align_up(ramdisk_size, page_size)
assert second_offset + second_size <= len(image)

digest = hashlib.sha1()
for offset, size in (
    (kernel_offset, kernel_size),
    (ramdisk_offset, ramdisk_size),
    (second_offset, second_size),
):
    digest.update(image[offset:offset + size])
    digest.update(struct.pack("<I", size))

# Android v0 boot image ID: payload components plus their little-endian sizes.
image[576:608] = digest.digest() + b"\0" * 12

result = bytes(image)
assert len(result) == expected_output_size
assert hashlib.sha256(result).hexdigest() == expected_output_sha256

with dst.open("xb") as output:
    output.write(result)

print(f"Created: {dst}")
print(f"Size: {len(result)}")
print(f"SHA-256: {hashlib.sha256(result).hexdigest()}")
print(f"Boot ID: {digest.hexdigest()}")
PY
```

Проверить созданный файл:

```sh
file files/twrp-mh2lm-3.7.1-rebuilt.img
sha256sum files/twrp-mh2lm-3.7.1-rebuilt.img
```

Ожидаются размер `47 796 224`, Android boot image header v0/page 4096 и SHA-256
`b31b0cd4b8ec417bedefec020d5f2216295ba4d9ae67ed9296f43beece6305d3`.
Если source hash или любой assert не совпал, **остановиться**: не ослаблять
проверки и не запускать получившийся файл на устройстве.

### Восстановление из точной копии

Если кандидат потерян, но `files/modded-twrp-g8x.img` сохранился и имеет
ожидаемый hash, это наиболее простой путь: скопировать его в новый путь
(например, `files/twrp-mh2lm-3.7.1-restored.img`) без перезаписи исходных
файлов, затем проверить SHA-256 и `cmp`. Если `modded-twrp-g8x.img` тоже
потерян, использовать предыдущий рецепт с donor `twrp-normal-mode.img`.

## 5. Почему не следует использовать другие локальные build-скрипты вслепую

В каталоге есть старые экспериментальные варианты. Их существование не
означает, что они создают проверенный рабочий образ.

- `files/mk_own_twrp.py` пишет `files/twrp-custom.img`, используя
  `files/boot_a-backup.img` как источник kernel/DTB и
  `files/twrp-normal-mode.img` как источник ramdisk; патчит
  `skip_initramfs -> want_initramfs` и собирает новый v0 header. Получившийся
  `files/twrp-custom.img` имеет hash
  `c426081f7f9761df74392c22dc884556ed7b8cc86bdc267f1185ca3822ef5848`, а не
  hash кандидата. Этот маршрут не подтверждён как рабочий touch fix и не
  воспроизводит кандидат.
- `files/mkbootimg_patch.py` предназначен для добавления токенов в cmdline;
  сам по себе он не снимает `androidboot.mode=normal` и не выдаёт проверенный
  кандидат.
- `files/twrp-iommu.img`, `files/twrp-skipinit.img`, `files/twrp-hybrid*.img`
  имеют другие SHA/параметры/header. Не подменять ими кандидат без повторной
  проверки загрузки и фактических событий тача.
- `files/modded-twrp-g8x-installer.zip` и
  `twrp-installer-v3.6.0-G8X_ab_TOUCHFIX.zip` не являются способом сборки.
  Проверенные update-binary/installer-процедуры затрагивают оба boot-слота.
  Они не использовались для описанного исправления; не запускать их для
  повторения RAM-проверки.

## 6. Что требуется для полной пересборки из исходников

Для сборки, если потеряны и образ-кандидат, и `twrp-normal-mode.img`, этой
папки недостаточно для гарантированного повторения исходного build. Нужно
сначала найти/зафиксировать:

1. точный source/release origin образа TWRP 3.7.1_12-0;
2. исходный kernel и полный build config/toolchain, соответствующие
   `4.14.340-openela-perf+`;
3. точный DTB, встроенный/переданный в boot image, и настройки его упаковки;
4. исходное дерево ramdisk TWRP, product/device configuration и все проприетарные
   файлы;
5. полный `repo manifest`, commit SHA каждого проекта, build flags, version
   strings и команду `mkbootimg`;
6. контрольные суммы всех скачанных inputs и результат сборки до любой
   проверки на телефоне.

Публичный репозиторий `tryhardkip/android_device_lge_mh2lm_twrp`, записанный в
локальном `ROMS.md`, относится к отдельному новому TWRP build path (manifest
`twrp-14.1`, современная Android/kernel ветка). Он не доказан как источник
именно установленного TWRP 3.7.1_12-0 и не гарантирует совпадение ядра,
ramdisk или тач-поведения. Использовать его можно только как новый кандидат,
не как воспроизводимый источник текущего образа.

Первоначально оценённая машина имела около 76 GB свободного места и 6.7 GiB
RAM; `repo` и `ninja` отсутствовали. Полная Android/TWRP сборка в этой работе
не выполнялась и её стоимость/совместимость не подтверждена. Точный бинарный
rebuild из donor выше не требует `repo`, `ninja` или Android build tree — только
Python 3 standard library.

## 7. Устройство: безопасная проверка без записи разделов

Этот раздел описывает только диагностику и RAM-тест. Он не разрешает
persistent-запись. Не выполнять `fastboot flash`, `fastboot set_active`,
установщик ZIP, TWRP Install или запись `boot_a`, `boot_b`, `dtbo_a`,
`dtbo_b`/любого другого раздела в рамках воспроизведения.

### 7.1. Перед тестом

1. Убедиться, что тест нужен и пользователь согласен на перезагрузку устройства
   в RAM Recovery.
2. Сверить SHA-256 и размер образа на хосте.
3. Перевести устройство в bootloader fastboot штатным способом для этой модели.
   Не использовать команды изменения слота.
4. Выполнить только чтение:

   ```sh
   fastboot getvar current-slot
   fastboot getvar product
   ```

5. Для воспроизведения известной конфигурации ожидается слот `b`/product
   `mh2lm`. Если слот не B, продукт не совпал или состояние неоднозначно —
   остановиться и запросить решение владельца. Не выполнять `set_active b`.

### 7.2. Только RAM-загрузка

Из корня проекта:

```sh
fastboot boot files/twrp-mh2lm-3.7.1-ramtest-candidate.img
```

`fastboot boot` передаёт образ для текущей загрузки и сам по себе не записывает
его в boot-раздел. Не заменять эту команду на `fastboot flash`. Успешный ответ
fastboot не доказывает ни полноценный вход в Recovery, ни работу touch; дождаться
ADB и проверить экран/версию:

```sh
adb wait-for-device
adb shell getprop ro.twrp.version
adb shell uname -a
adb shell cat /proc/cmdline
```

`/proc/cmdline` в некоторых сессиях может быть недоступен. Если так, записать
отказ доступа и продолжить только по доступным данным; не трактовать
недоступность как отсутствие параметра.

Ожидаемые ориентиры для известного кандидата: TWRP `3.7.1_12-0`, kernel
`4.14.340-openela-perf+`; при известной конфигурации B наблюдался
`androidboot.dtbo_idx=5`.

### 7.3. Проверка touch input и реальные касания

Сначала обнаружить устройство по имени, не по фиксированному `eventN`:

```sh
adb shell cat /proc/bus/input/devices
adb shell getevent -lp
```

Найти `Name="touch_dev"` и соответствующий ему `/dev/input/eventN`. Проверить
`BTN_TOUCH`, `BTN_TOOL_FINGER`, multitouch `ABS_MT_POSITION_X/Y`, диапазоны
примерно X `0..1079`, Y `0..2339` и `INPUT_PROP_DIRECT`. Это подтверждает
регистрацию input-устройства, но ещё не подтверждает события.

Затем запустить ограниченный capture и попросить пользователя коснуться
экрана/провести пальцем именно во время записи. Подставить найденный event:

```sh
capture="files/touchfix-capture-$(date +%Y%m%d-%H%M%S).txt"
test ! -e "$capture" || { echo "Файл уже существует: $capture"; exit 1; }
timeout 30s adb shell getevent -lt /dev/input/eventN \
  | tee "$capture"
```

Успешная запись должна содержать фактические строки `BTN_TOUCH` с переходами
нажатия/отпускания и значения `ABS_MT_POSITION_X/Y`. Обычный код завершения 124
от host `timeout` означает, что истёк лимит capture, а не что touch сработал.
Нулевой output может означать, что в интервале не было касаний, неверно выбран
event node либо события не поступили; сначала сопоставить с ручным касанием и
`getevent -lp`, затем описать результат. Не называть пустой capture успешным.

## 8. Диагностическая история и вероятный, но не доказанный старый механизм

На прежнем TWRP 3.6.0_11-0 с kernel `4.14.223-perf+` `touch_dev` мог быть
зарегистрирован, но 60-секундный `getevent` не показывал событий. В `dmesg`
наблюдались:

```text
s3618_suspend: Etc boot_mode(7)!!!
s3618_resume: Etc boot_mode(7)!!!
s3618_power, off
```

В исходниках некоторых старых веток именно `mh2lm` enum задаёт
`TOUCH_RECOVERY_MODE=7`, а `s3618_suspend()`/`s3618_resume()` обрабатывают
Recovery вместе с LAF/charger и отключают питание/IRQ. Это делает boot-mode
объяснением правдоподобным для той старой версии, но точный source commit для
бинарного ядра 4.14.223 не найден. Не переносить этот вывод автоматически на
kernel `4.14.340-openela-perf+` текущего TWRP.

Ссылки, использованные для исторического сравнения:

- `ronaxdevil/android_kernel_lge_mh2lm`, commit
  `f45265ab440db22eefa59dfcafaa949fe7c8fb0c`:
  [touch_s3618.c](https://github.com/ronaxdevil/android_kernel_lge_mh2lm/blob/f45265ab440db22eefa59dfcafaa949fe7c8fb0c/drivers/input/touchscreen/lge/synaptics/s3618/touch_s3618.c)
  и [touch_core.h](https://github.com/ronaxdevil/android_kernel_lge_mh2lm/blob/f45265ab440db22eefa59dfcafaa949fe7c8fb0c/drivers/input/touchscreen/lge/touch_core.h);
- upstream SM8150 commit `eeec3bb02bf2711b9035ca07b12f52df210bb036`:
  [touch_ftm4.c](https://github.com/sidex15/android_kernel_lge_sm8150/blob/eeec3bb02bf2711b9035ca07b12f52df210bb036/drivers/input/touchscreen/lge/stm/touch_ftm4.c).

Эти ссылки не подтверждают точное соответствие исходника запущенному
4.14.223/4.14.340 бинарному ядру.

## 9. История постоянной установки и readback

Ниже — журнал уже произошедшего изменения, а не инструкция повторять его:

1. До изменений сделаны полные read-only копии `boot_a`, `boot_b`, `dtbo_a`,
   `dtbo_b` (таблица в §3.3).
2. Для сравнения кандидат временно записывался в `boot_a`, слот A активировали.
   При `dtbo_idx=3` `touch_dev` отсутствовал, даже после загрузки Recovery.
3. `boot_a` восстановили из точного baseline; полный readback hash совпал.
4. На активном B кандидат проверили RAM-загрузкой: `dtbo_idx=5`, появился
   `touch_dev`, сохранена event-трасса.
5. После прямого разрешения владельца кандидат записали в `boot_b`, B оставили
   активным и загрузили Recovery. `dtbo` не записывали.
6. После записи первые 47 796 224 байта `boot_b` побайтно совпадали с кандидатом.
   Полный post-write hash всех 100 663 296 байт `boot_b` не снимался; не
   придумывать и не заявлять его. Полная исходная копия `boot_b` сохранена.
7. Пользователь подтвердил, что после обычной перезагрузки текущего TWRP на B
   сенсор работает.

Текущий успешный статус не является разрешением на новые записи. Если позже
потребуется постоянное изменение, сначала требуется отдельное явное решение
владельца и новый, безопасный план с проверенными резервными копиями.

## 10. Устаревшие/опасные пути

- Не использовать установщик
  `files/modded-twrp-g8x-installer.zip`: его `update-binary` выбирает `boot`,
  если не найден отдельный `recovery_b`, затем записывает `_a` и `_b`.
- Не использовать `twrp-installer-v3.6.0-G8X_ab_TOUCHFIX.zip`: его цикл
  обрабатывает оба boot-слота.
- Не прошивать DTBO «для совпадения» с кандидатом: рабочая проверка была с
  существующим `dtbo_b`, а не с новым DTBO.
- Не менять active slot ради удобства теста. Проверять только текущий B; если
  устройство не в B — остановиться.
- Не полагаться на `touch_dev` как единственный критерий: для успеха нужны
  реальные `getevent`-события либо прямое подтверждение пользователя. Идеально
  сохранить и то и другое.

## 11. Чек-лист передачи следующему агенту

1. Прочитать этот документ, затем `TOUCH_DIAGNOSIS_2026-11-17.md` для полной
   временной шкалы и `README_TOUCHFIX (1).md` для краткого пользовательского
   статуса.
2. До действий проверить наличие образов и совпадение SHA-256 с §3.1.
3. Если основной образ утерян, сначала проверить точную копию
   `files/modded-twrp-g8x.img`; иначе использовать проверенный rebuild из
   `files/twrp-normal-mode.img` (§4).
4. Если донор тоже отсутствует, остановиться: исходники/манифест текущего
   kernel+ramdisk не закреплены. Не собирать произвольное ядро и не выдавать его
   за прежний образ.
5. Device test — только если он нужен: проверить, что слот уже B, выполнить
   `fastboot boot`, найти `touch_dev`, захватить реальные события во время
   касания. Никаких persistent-команд.
6. Отчёт должен отдельно указать: exact image hash, версию TWRP/kernel,
   фактический слот и `dtbo_idx` (если доступен), input node, наличие/отсутствие
   реальных `BTN_TOUCH`/X/Y строк и состояние пользовательского подтверждения.

## 12. Связанные документы и артефакты

- [Краткий статус и предупреждения](README_TOUCHFIX.md)
- [Подробная историческая диагностика и readback](TOUCH_DIAGNOSIS_2026-11-17.md)
- Рабочий образ: `files/twrp-mh2lm-3.7.1-ramtest-candidate.img`
- Точная копия: `files/modded-twrp-g8x.img`
- Проверенный donor для восстановления: `files/twrp-normal-mode.img`
- Сохранённые реальные касания: `files/touchfix-slotb-getevent.txt`
- Read-only baseline: `files/*-readonly-baseline-20261117.img`
- RAM-only launcher: `start-twrp.sh` (отказывает на аргументе `--flash`)
