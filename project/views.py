from flask import Blueprint, request, jsonify

from .tasks import create_crawl, process_crawl, get_crawl

main = Blueprint('main', __name__)


@main.route('/crawl', methods=['POST'])
def crawl() -> jsonify:
    """
    Handle the crawl request.

    :return: JSON response with crawl IDs or error message.
    """
    json = request.json

    if 'urls' not in json or not json['urls']:
        return jsonify({'error': 'URLs are missing, or not specified well, check argument urls'}), 400

    crawl_ids = []
    for url in json['urls']:
        crawl_id = create_crawl(url)
        crawl_ids.append(str(crawl_id))

    return jsonify({'crawl_ids': ','.join(crawl_ids)}), 200


@main.route('/recrawl/<int:crawl_id>', methods=['GET'])
def re_crawl(crawl_id) -> jsonify:
    """
    Manually re-crawl an existing record.

    :param crawl_id: The ID of the crawl.
    :return: JSON response with crawl status or error message.
    """
    crawl_obj = get_crawl(crawl_id=crawl_id)
    if not crawl_obj:
        return jsonify({'error': 'Crawl ID not found.'}), 404
    else:
        process_crawl.delay(crawl_obj.id)
        return jsonify({'crawl_ids': crawl_obj.id}), 200


@main.route('/status/<int:crawl_id>', methods=['GET'])
def get_status(crawl_id) -> jsonify:
    """
    Get the status of a crawl.

    :param crawl_id: The ID of the crawl.
    :return: JSON response with crawl status or error message.
    """
    crawl_obj = get_crawl(crawl_id=crawl_id)
    if not crawl_obj:
        return jsonify({'error': 'Crawl ID not found.'}), 404
    elif crawl_obj.status == 'Complete':
        return jsonify({'status': crawl_obj.status, 'html': crawl_obj.html}), 200
    else:
        return jsonify({'status': crawl_obj.status}), 200
