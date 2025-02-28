import re
import toml
import json
import numpy as np
from time import time
from datetime import datetime
from pandas import DataFrame, Series
from statschat.llm import Inquirer
from statschat.utils import deduplicator
from rapidfuzz import fuzz


# TODO: This template doesn't really match
template = {
    "questions": "how many people watched the kings coronation",
    "should_answer": True,
    "answer_provided": True,
    "test_answer_provided": "Pass",
    "expected_answer": "around 1 in 6 (59%)",
    "answer": "Around 1 in 6 people watched the kings coronation",
    "fuzzy_partial_token_ratio": 100,
    "test_correct_answer": "Pass",  # TODO
    "should_provide_relevant": True,
    "section_url": "http:/www.ons.gov.uk/{publication link}",
    "page_content": "...[some text]...",
    "expected_keywords": ["watched", "coronation", "king", "queen"],
    "expected_url": "some_url_to_main_bulletin",
    "all_urls": ["top_url", "next_url", "etc"],
    "test_article_relevant": "Pass",  # TODO
    "seconds_to_run": 6.53,
    "retriever": "haystack.nodes.retriever.sparse.BM25Retriever",
    "reader": "haystack.nodes.reader.farm.FARMReader",
    "reader_model": "deepset/bert-large-uncased-whole-word-masking-squad2",
    "answer_model": "google/flan-t5-large",
    "confidence_threshold": 0.03,
}


def _get_one_first_response(question: str, searcher) -> dict:
    """get the first response from a question
    Parameters
    ----------
    question:str
        a question to pass to the query
    searcher
        a searcher class object
    k_docs: int
        number of documents for the retriver to return for the reader
    k_answer: int
        number of answers the reader provides the summarizer
    Returns
    -------
    dict
        dictionary of response objects (answer, confidence, references)
    """
    # start_time = time()
    # response = searcher(question)
    # run_time_seconds = round(time() - start_time, 2)
    # first_response = response[0]
    # first_response["seconds_to_run"] = run_time_seconds
    start_time = time()
    first_response = searcher(question)
    run_time_seconds = round(time() - start_time, 2)
    first_response["seconds_to_run"] = run_time_seconds
    return first_response


def _get_first_responses(questions: list, searcher):
    """get first responses from each question
    Parameters
    ----------
    questions:list
        a list of questions to get responses from
    searcher
        the searcher class object
    k_docs: int
        number of documents for the retriver to return for the reader
    k_answer: int
        number of answers the reader provides the summarizer
    Returns
    -------
    list
        a list of the first response objects"""
    first_responses = [
        _get_one_first_response(question, searcher) for question in questions
    ]
    return first_responses


def get_test_responses(questions: list, searcher) -> list:
    """retrieve the first query responses for all questions
    Parameters
    ---------
    questions:list
        a list of questions to query
    searcher
        a searcher class object
    k_docs: int
        number of documents for the retriver to return for the reader
    k_answer: int
        number of answers the reader provides the summarizer
    Returns
    -------
    list
        list of dictionaries containing responses from each test
    """
    first_responses = _get_first_responses(questions, searcher)
    test_responses = [
        _get_response_components(response) for response in first_responses
    ]
    return test_responses


def _get_response_components(response: dict) -> dict:
    """extract important response components for testing
    Parameters
    ----------
    response: dict
        complete dictonary of response objects
    Returns
    -------
    dict
        selected response components (answer, confidence,
        section_url, answer_provided)
    """
    response_components = {
        "answer": response["answer"],
        "section_url": response["references"][0]["section_url"],
        "all_urls": [x["section_url"] for x in response["references"]],
        "page_content": response["references"][0]["page_content"],
        "seconds_to_run": response["seconds_to_run"],
    }
    return response_components


def test_answer_provided(
    meta_test_responses: DataFrame, question_config: dict
) -> DataFrame:
    """
    Parameters
    ----------
    meta_test_responses: DataFrame
        a dataframe of test responses with searcher information
    question_config: dict
        the question configuration dictionary
    Returns
    -------
    DataFrame
        a dataframe with columns confirming whether the questions that
        were supposed to be answered met that criteria
    """
    question_info = _add_question_info(meta_test_responses, question_config)
    question_info["answer_provided"] = question_info["answer"].apply(
        _check_answer_provided
    )
    question_info["test_answer_provided"] = _test_series_value_match(
        question_info["should_answer"], question_info["answer_provided"]
    )
    question_info["fuzzy_partial_ratio"] = _partial_token_set_ratio_rowwise(
        question_info, "expected_answer", "answer"
    )
    return question_info


def _add_question_info(dataframe: DataFrame, question_config: dict) -> DataFrame:
    """add question info from config to dataframe
    Parameters
    ----------
    dataframe: DataFrame
        a dataframe which you want to append questions to
    question_config: dict
        the question configuration dictionary
    Returns
    -------
    DataFrame
        a dataframe with the question info appended
    """
    dataframe["questions"] = question_config.keys()
    question_fields = [
        "should_answer",
        "should_provide_relevant",
        "expected_keywords",
        "expected_answer",
        "expected_url",
    ]
    for field in question_fields:
        dataframe[field] = _get_nested_dict_element(field, question_config)
    return dataframe


def _get_nested_dict_element(dict_key: str, dictionary: dict) -> list:
    """get value from nested dictionary using 2nd order key
    Parameters
    ----------
    dict_key: str
        key for nested dictionary
    dictionary: dict
        dictionary containing another dictionary
    Returns
    -------
        value of the nested dictionary which corosponds to the given key
    """
    nested_dict_element = [
        value[dict_key] for value in dictionary.values() if dict_key in value
    ]
    return nested_dict_element


def _check_answer_provided(answer: str) -> bool:
    """check answer for fail response string
    Parameters
    ----------
    answer: str
        answer string from the query response

    Returns
    -------
    bool
        True if answer is not the string for failed answer"""
    if bool(re.match("NA", answer)):
        answer_provided = False
    else:
        answer_provided = True
    return answer_provided


def _test_series_value_match(reference: Series, comparison: Series) -> Series:
    """rowwise comparison of two series to check if they have the same values
    in a given row
    Parameters
    ----------
    reference: Series
        the reference series for comparison
    comparison: Series
        the comparison series for comparison
    Returns
    -------
    Series
        a series of 'pass' or 'fail' strings
    """
    new_series = Series(np.where(reference == comparison, True, False))
    return new_series


def _partial_token_set_ratio_rowwise(
    dataframe: DataFrame, column_1: str, column_2: str
) -> Series:
    """map the partial token set ratio function across two columns of a dataframe
    Parameters
    ----------
    dataframe: Dataframe
        dataframe with two columns you want to compare
    column_1: string
        name of the first column
    column_2: string
        name of the second column
    Returns
    -------
    Series
        series of partial ratio scores
    """
    ratio = Series(
        map(fuzz.partial_token_set_ratio, dataframe[column_1], dataframe[column_2])
    )
    return ratio


def score_retrieval(text: str, tokens: list[str]) -> float:
    """
    Crude measure of retrieval accuracy, are the expected keywords present?
    Normalises to fraction of keywords present, for comparisons between docs.

    Parameters
    ----------
    text: str
        The piece of text to be scored
    tokens: list[str]
        A list of expected (lowercase) tokens/words

    Returns
    -------
    float
        score, between 1 (perfect recall) and 0
    """
    text_clean = text.lower()
    return sum([token in text_clean for token in tokens]) / len(tokens)


def check_url(expected: str, actual: str) -> bool:
    """Check if the expected url present in that returned."""
    return str(expected) in str(actual)


def mmr_url(expected_url: str, returned_urls: list[str]) -> float:
    """
    Score rank of expected result within retrieved docs.  Score is 1 / rank
    of the expected document.  We use the URL's of documents as unique
    identifiers here.  Score is 0.0 if not found.

    Parameters
    ----------
    expected_url: str
        The anticipated URL of the top retrieved document, what we want to see
    returned_urls: list[str]
        The URL's of the documents actually returned by the search

    Returns
    -------
    float
        A score between 0 (not found) and 1 (top-ranked)
    """
    # Handles case, no returns expected
    if not expected_url:
        if len(returned_urls) > 0:
            return 0.0
        return 1.0

    # Returns 1/rank if expected url is present in results
    for i, url in enumerate(returned_urls):
        if expected_url in url:
            return 1.0 / (i + 1.0)

    # Returns zero if no match in search results
    return 0.0


def test_search_result(df):
    """Handles tests relating to accuracy of doc retrieval system."""
    df["retrieval_keyword_score"] = df.apply(
        lambda row: score_retrieval(row["page_content"], row["expected_keywords"]),
        axis=1,
    )
    df["correct_doc"] = df.apply(
        lambda row: check_url(row["expected_url"], row["section_url"]), axis=1
    )
    df["retrieval_rank"] = df.apply(
        lambda row: mmr_url(row["expected_url"], row["all_urls"]), axis=1
    )
    return df


def pipeline(app_config_file: str = "app_config.toml", n_questions: int = None):
    """main pipeline function for the evaluator"""
    question_config = toml.load(
        "statschat/model_evaluation/question_configuration.toml"
    )

    # Optionally only run N questions (useful for quick test/eval)
    if n_questions:
        question_config = {
            key: value for key, value in list(question_config.items())[:n_questions]
        }

    # Create app components
    app_config = toml.load(app_config_file)
    searcher = Inquirer(**app_config["db"], **app_config["search"])

    def make_query(question: str) -> dict:
        """Utility, wrap all search functionality into one."""
        docs = searcher.similarity_search(question)
        answer = searcher.query_texts(question, docs)
        print(question)
        print(len(docs))
        print(answer)
        results = {
            "answer": answer,
            "references": deduplicator(docs, keys=["section_url", "title"]),
        }
        return results

    test_responses = get_test_responses(question_config.keys(), searcher=make_query)
    test_response_df = DataFrame(test_responses)
    print(test_response_df.head())
    question_info = test_answer_provided(test_response_df, question_config)
    question_info = test_search_result(question_info)
    question_info["app_config"] = str(app_config)

    metrics = {
        "retrieval_keyword": question_info["retrieval_keyword_score"].mean(),
        "retrieval_rank": question_info["retrieval_rank"].mean(),
        "retrieval_correct": question_info["correct_doc"].mean(),
        "answer_fuzz": question_info["fuzzy_partial_ratio"].mean(),
        "answer_present": question_info["test_answer_provided"].mean(),
    }

    col_order = [
        "questions",
        "should_answer",
        "answer_provided",
        "test_answer_provided",
        "expected_answer",
        "answer",
        "fuzzy_partial_ratio",
        "expected_url",
        "retrieval_keyword_score",
        "correct_doc",
        "retrieval_rank",
        "should_provide_relevant",
        "section_url",
        "all_urls",
        "page_content",
        "expected_keywords",
        "seconds_to_run",
        "app_config",
    ]
    stamp = datetime.now()
    question_info[col_order].to_csv(
        f"data/test_outcomes/{format(stamp, '%Y-%m-%d_%H:%M')}_questions.csv",
        index=False,
    )
    # TODO: Should we just copy and rename the TOML rather than change format?
    with open(
        f"data/test_outcomes/{format(stamp, '%Y-%m-%d_%H:%M')}_config.json", "w"
    ) as f:
        json.dump(app_config, f, indent=4)
    return metrics


if __name__ == "__main__":
    pipeline(app_config_file="app_config.toml")


# TODO consider alternative tests for answer correctness
# TODO conduct relevance scoring on more than the first returned article
# TODO add a field to capture other relevant parameters
# TODO create a new script for joining multiple test output csvs
