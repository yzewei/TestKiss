import time
from app import app
from app.Models.RunModel import Run
from app.Models.RepModel import Rep
from app.Models.ProductModel import Product
from app.Models.ProductModel import ProductVersion
from flask_login import login_required, current_user
from flask import Blueprint, request, redirect, url_for, render_template, flash
from app.Common.Utils import get_query_url, common_response, get_mongo_index, list_mongo_res


rep = Blueprint('rep', __name__)


@rep.route('/', methods=['GET'])
@login_required
def product():
        r = request.args
        pd = Product()
        page = r.get('page', 1)
        size = r.get('size', 16)
        if page is None:
            page = 1
        search = r.get('search', None)
        if search is None:
            search = {}
        else:
            search = {
                "name": {
                    "$regex": search
                }
            }
        products = pd.get_list(search, page, size)
        params = get_query_url(request)
        return render_template('rep/choose_pd.html', products=products, url=request.path, params=params)


@rep.route('/list', methods=['GET'])
@login_required
def lists():
        r = request.args
        pl = Rep()
        pd = Product()
        page = r.get('page', 1)
        if page is None:
            page = 1
        size = r.get('size', 10)
        if size is None:
            size = 10
        product_id = r.get('product_id', '')
        if product_id == "":
            flash("产品 product_id 不能为空!")
            return redirect(url_for('rep.product'))
        prod = pd.table.find_one({"_id": int(product_id)})
        if prod is None:
            flash("产品不存在，请重新选择!")
            return redirect(url_for('rep.product'))
        search = r.get('search', None)
        if search is None:
            search = {
                "pd": product_id
            }
        else:
            search = {
                "pd": product_id,
                "name": {
                    "$regex": search
                }
            }
        reps = pl.get_list(search, int(page), int(size))
        params = get_query_url(request)
        return render_template('rep/rep.list.html', product=prod, reps=reps, url=request.path, params=params)


@rep.route('/add', methods=['GET', 'POST'])
def add():
    pl = Rep()
    pv = ProductVersion()
    if request.method == "GET":
        r = request.args
        pd = Product()
        product_id = r.get('product_id', '')
        pd_ver = pv.table.find({"pd": product_id}, {"ver": 1}).sort([("_id", -1)]).limit(20)
        prod = pd.table.find_one({"_id": int(product_id)})
        return render_template('rep/rep.add.html', product=prod, versions=pd_ver)

    if request.method == "POST":
        r = request.form
        name = r.get('rep_name', '')
        product_id = r.get('product_id', '')
        pd_ver = r.get('pd_ver', '')
        rep_type = r.get('rep_type', '')
        rep_detail = r.get('rep_detail', '')
        err = {}
        if name.strip() == "":
            err['name'] = "计划名称不能为空!"
        if product_id.strip() == "":
            err['product_id'] = "产品ID不能为空!"
        if pd_ver.strip() == "":
            err['pd_ver'] = "产品版本不能为空！"
        if rep_type.strip() == "":
            err['rep_type'] = "计划类型不能为空!"
        if rep_detail.strip() == "":
            err['rep_detail'] = "计划详情不能为空!"
        if len(err) > 0:
            return common_response(data=err, err=500, msg="参数错误，请查看接口返回!")
        try:
            d = {
                "_id": get_mongo_index('reps'),
                "name": name,
                "pd": product_id,
                "pd_ver": pd_ver,
                "type": rep_type,
                "detail": rep_detail,
                "author": current_user.username,
                "create_time": time.time(),
                "update_time": time.time()
            }
            data = pl.table.insert_one(d)
            return common_response(data={"_id": data.inserted_id}, err=0, msg="添加成功！")
        except Exception as e:
            app.logger.error(str(e))
            return common_response(data='', err=500, msg='添加失败')


@rep.route('/detail', methods=['GET'])
@login_required
def detail():
    r = request.args
    rep_id = r.get('rep_id', '')
    product_id = r.get('product_id', '')
    if rep_id.strip() == "":
        flash("rep_id 不能为空！")
        return redirect(request.referrer)
    pd = Product()
    pl = Rep()
    prod = pd.table.find_one({"_id": int(product_id)})
    data = pl.table.find_one({"_id": int(rep_id)})
    return render_template('rep/rep.detail.html', rep=data, product=prod)


@rep.route('/del', methods=['DELETE'])
@login_required
def delete():
    r = request.form
    pl = Rep()
    rc = Run()
    _id = r.get("_id", '')
    if _id.strip() == "":
        return common_response(data='', err=500, msg='_id 参数不能为空!')
    check = rc.table.find_one({"pl": _id})
    if check is not None:
        return common_response(data='', err=500, msg="计划下有执行，请先删除执行!")
    try:
        data = pl.table.delete_one({"_id": int(_id)})
        return common_response(data=data.raw_result, err=0, msg='删除成功!')
    except Exception as e:
        app.logger.error(str(e))
        return common_response(data='', err=500, msg="删除失败!")


@rep.route('/update', methods=['GET', 'PUT'])
@login_required
def update():
    pl = Rep()
    pv = ProductVersion()
    if request.method == "GET":
        r = request.args
        pd = Product()
        product_id = r.get('product_id', '')
        rep_id = r.get('rep_id', '')
        pd_ver = pv.table.find({"pd": product_id}, {"ver": 1}).sort([("_id", -1)]).limit(20)
        data = pl.table.find_one({"_id": int(rep_id)})
        prod = pd.table.find_one({"_id": int(product_id)})
        return render_template('rep/rep.edit.html', product=prod, versions=pd_ver, rep=data)

    if request.method == "PUT":
        r = request.form
        rep_id = r.get('rep_id', '')
        name = r.get('rep_name', '')
        product_id = r.get('product_id', '')
        pd_ver = r.get('pd_ver', '')
        rep_type = r.get('rep_type', '')
        rep_detail = r.get('rep_detail', '')
        err = {}
        if rep_id.strip() == "":
            err['rep_id'] = "rep_id 不能为空!"
        if name.strip() == "":
            err['name'] = "计划名称不能为空!"
        if product_id.strip() == "":
            err['product_id'] = "产品ID不能为空!"
        if pd_ver.strip() == "":
            err['pd_ver'] = "产品版本不能为空！"
        if rep_type.strip() == "":
            err['rep_type'] = "计划类型不能为空!"
        if rep_detail.strip() == "":
            err['rep_detail'] = "计划详情不能为空!"
        if len(err) > 0:
            return common_response(data=err, err=500, msg="参数错误，请查看接口返回!")
        try:
            q = {"_id": int(rep_id)}
            d = {
                "$set": {
                    "name": name,
                    "pd_ver": pd_ver,
                    "type": rep_type,
                    "detail": rep_detail,
                    "update_time": time.time()
                }
            }
            data = pl.table.update_one(q, d)
            return common_response(data={"result": data.raw_result}, err=0, msg="更新成功！！")
        except Exception as e:
            app.logger.error(str(e))
            return common_response(data='', err=500, msg='更新失败！')


@rep.route('/query', methods=['GET'])
def query():
    r = request.args
    pl = Rep()
    pd = r.get('pd', '').strip()
    ver = r.get('pd_ver', '').strip()
    try:
        data = pl.table.find({"pd": pd, "pd_ver": ver})
        data = list_mongo_res(data)
        return common_response(data=data, err=0, msg="请求成功！")
    except Exception as e:
        app.logger.error(str(e))
        return common_response(data='', err=500, msg="请求失败!")
