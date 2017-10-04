"平成26年度版"

import requests
from bs4 import BeautifulSoup


class Special_Subject:
    "専門系科目"
    special_basic_subject = 0
    sbs_str = '専門基礎科目'
    special_subject = 0
    ss_str = '専門科目'
    special_related_subject = 0
    srs_str = '関連専門科目'

    def __init__(self, summary_dict):
        self.special_basic_subject = summary_dict[self.sbs_str]
        self.special_subject = summary_dict[self.ss_str]
        self.special_related_subject = summary_dict[self.srs_str]

    def check(self):
        insufficient_subject = []

        def append_if_lt(subject_score, needed_score, subject_str):
            if subject_score < needed_score:
                insufficient_subject.append((subject_str,
                                             needed_score - subject_score))

        append_if_lt(self.special_basic_subject, 44, self.sbs_str)
        append_if_lt(self.special_subject, 31, self.ss_str)
        append_if_lt(self.special_related_subject, 6, self.srs_str)

        return insufficient_subject


class Educational_Subject:
    "全学教育科目"

    basic_subject = 0  # 全学基礎科目の単位
    bunkei_subject = 0  # 文系科目の単位、英語での表現がいいのない
    science_basic_subject = 0  # 理系基礎科目
    science_cultural_subject = 0  # 理系教養科目
    zengaku_cultural_subject = 0  # 全学教養科目+開放科目

    def __init__(self, summary_dict):
        self.basic_subject = summary_dict['基礎セミナー'] + summary_dict['言語文化'] + \
            summary_dict['健康・スポーツ科学（実習）'] + summary_dict['健康・スポーツ科学（講義）']
        self.bunkei_subject = summary_dict['文系基礎科目'] + summary_dict['文系教養科目']
        self.science_basic_subject = summary_dict['理系基礎科目']
        self.science_cultural_subject = summary_dict['理系教養科目']
        self.zengaku_cultural_subject = summary_dict['開放科目'] + \
            summary_dict['全学教養科目']

    def check(self):
        insufficient_subject = []

        def append_if_lt(subject_score, needed_score, subject_str):
            if subject_score < needed_score:
                insufficient_subject.append((subject_str,
                                             needed_score - subject_score))

        append_if_lt(self.basic_subject, 16, "全学基礎科目")
        append_if_lt(self.bunkei_subject, 4, "文系科目")
        append_if_lt(self.science_basic_subject, 23, "理系基礎科目")
        append_if_lt(self.science_cultural_subject, 4, "理系教養科目")
        append_if_lt(self.zengaku_cultural_subject, 2, "全学教養科目")

        sum = self.basic_subject + self.bunkei_subject + self.science_basic_subject + \
            self.science_cultural_subject + self.zengaku_cultural_subject
        append_if_lt(sum, 55, "合計")

        return insufficient_subject


# HACK: dirty work
class Subject:
    special_subject = None
    educational_subject = None

    def __init__(self, summary_dict):
        self.special_subject = Special_Subject(summary_dict)
        self.educational_subject = Educational_Subject(summary_dict)

    def check(self):
        return self.special_subject.check() + self.educational_subject.check()


def table_dict(bs_table):
    td_list = map(lambda tr: tr.find_all('td'), bs_table.find_all('tr'))
    return dict(
        map(lambda tds: (tds[0].text.strip()[1:], float(tds[1].text.strip())),
            td_list))


def get_summary_score(url):
    bs = BeautifulSoup(requests.get(url).text, "html.parser")
    return Subject(table_dict(bs.find_all('table')[2]))


def main(url):
    print("足りない分")

    for subject, score in get_summary_score(url).check():
        print(subject + ": " + str(score))

    return


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("履修ページのURL")
        exit()

    main(sys.argv[1])
