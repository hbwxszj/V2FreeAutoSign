import argparse
import json
import logging
from logging.handlers import RotatingFileHandler

import requests


class Constants:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Content-Type": "application/json;charset=utf-8",
    }
    login_url = "https://w1.v2free.net/auth/login"
    sign_url = "https://w1.v2free.net/user/checkin"


def get_logger(
    file_name: str = "flow.log", max_bytes: int = 1024, backup: int = 2
) -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
    filehandler = RotatingFileHandler(
        file_name, mode="a", maxBytes=max_bytes, backupCount=backup, encoding="utf-8"
    )
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    return logger


def masked_email(email):
    length = len(email)
    at_index = email.rfind("@")
    dot_index = email.rfind(".")
    return (
        email[0].ljust(at_index, "*")
        + email[at_index : at_index + 2]
        + email[dot_index:length].rjust(length - at_index - 2, "*")
    )


def parse_info():
    parser = argparse.ArgumentParser(description="V2ray签到脚本")
    parser.add_argument("--username", type=str, help="账号")
    parser.add_argument("--password", type=str, help="密码")
    args = parser.parse_args()
    return json.dumps(
        {
            "email": args.username,
            "passwd": args.password,
            "code": "",
        },
        ensure_ascii=False,
    ).encode("utf-8")


def record_info(string: str, logger: logging.Logger, stage: str) -> bool:
    try:
        logger.info(json.loads(string))
        return True
    except Exception as e:
        logger.info(f"{stage}阶段出现异常,请确认账号信息是否正确:{repr(e)}")
    return False


def main():
    logger = get_logger()
    data = parse_info()
    client = requests.Session()
    response = client.post(Constants.login_url, data=data, headers=Constants.headers)
    if not record_info(response.text, logger, stage="登录"):
        return
    response = client.post(Constants.sign_url, headers=Constants.headers)
    record_info(response.text, logger, stage="签到")


if __name__ == "__main__":
    main()
