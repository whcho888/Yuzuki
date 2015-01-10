# -*- coding: utf-8 -*-
from sqlalchemy.orm import subqueryload

from config import ARTICLE_PER_PAGE, REPLY_PER_PAGE
from exception import BadArgument
from helper.resource import YuzukiResource
from helper.sphinxsearch import search_article, search_reply
from helper.template import render_template
from model.article import Article
from model.board import Board
from model.reply import Reply
from model.user import User


class Search(YuzukiResource):
    def render_GET(self, request):
        query_string = request.get_argument("query")
        search_type = request.get_argument("type", "content")
        target = request.get_argument("target", "article")
        if search_type not in ["user", "content"] or target not in ["article", "reply"]:
            raise BadArgument("type", search_type)

        board_name = request.get_argument("board", None)
        if board_name:
            query = request.dbsession.query(Board).filter(Board.name == board_name)
            result = query.all()
            if not result:
                raise BadArgument("board", board_name)
            board = result[0]
        else:
            board = None

        try:
            page = int(request.get_argument("page", "1"))
        except ValueError:
            raise BadArgument("page", request.get_argument("page"))

        if search_type == "content":
            if target == "article":
                query = search_article(request.dbsession, query_string, board).options(subqueryload(Article.board))
            else:
                query = search_reply(request.dbsession, query_string, board).options(
                    subqueryload(Reply.article).subqueryload(Article.board))
        else:
            query = self.request.dbsession.query(User).filter(User.nickname == query_string)
            result = query.all()
            if not result:
                query = []
            else:
                target_user = result[0]
                if target == "article":
                    query = self.request.dbsession.query(Article).filter(Article.user == target_user).options(
                        subqueryload(Article.board))
                else:
                    query = self.request.dbsession.query(Reply).filter(Reply.user == target_user).options(
                        subqueryload(Reply.article).subqueryload(Article.board))

        item_per_page = ARTICLE_PER_PAGE if target == "article" else REPLY_PER_PAGE
        start_idx = item_per_page * (page - 1)
        end_idx = item_per_page * page
        items = query[start_idx:end_idx]
        render_page = "search_article.html" if target == "article" else "search_reply.html"
        context = {"items": items}
        return render_template(render_page, request, context)