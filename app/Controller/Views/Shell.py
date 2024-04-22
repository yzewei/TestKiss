import time
from app import app
from app.Models.RunModel import Run
from app.Models.ShellModel import Shell
from app.Models.ProductModel import Product
from app.Models.ProductModel import ProductVersion
from flask_login import login_required, current_user
from flask import Blueprint, request, redirect, url_for, render_template, flash
from app.Common.Utils import get_query_url, common_response, get_mongo_index, list_mongo_res


shell = Blueprint('shell', __name__)


@shell.route('/', methods=['GET'])
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
        return render_template('shell/choose_pd.html', products=products, url=request.path, params=params)


@shell.route('/list', methods=['GET'])
@login_required
def lists():
        r = request.args
        pl = Shell()
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
            return redirect(url_for('shell.product'))
        prod = pd.table.find_one({"_id": int(product_id)})
        if prod is None:
            flash("产品不存在，请重新选择!")
            return redirect(url_for('shell.product'))
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
        shells = pl.get_list(search, int(page), int(size))
        params = get_query_url(request)
        return render_template('shell/shell.list.html', product=prod, shells=shells, url=request.path, params=params)


@shell.route('/add', methods=['GET', 'POST'])
def add():
    pl = Shell()
    pv = ProductVersion()
    if request.method == "GET":
        r = request.args
        pd = Product()
        product_id = r.get('product_id', '')
        pd_ver = pv.table.find({"pd": product_id}, {"ver": 1}).sort([("_id", -1)]).limit(20)
        prod = pd.table.find_one({"_id": int(product_id)})
        return render_template('shell/shell.add.html', product=prod, versions=pd_ver)

    if request.method == "POST":
        r = request.form
        name = r.get('shell_name', '')
        product_id = r.get('product_id', '')
        pd_ver = r.get('pd_ver', '')
        shell_type = r.get('shell_type', '')
        shell_detail = r.get('shell_detail', '')
        err = {}
        if name.strip() == "":
            err['name'] = "计划名称不能为空!"
        if product_id.strip() == "":
            err['product_id'] = "产品ID不能为空!"
        if pd_ver.strip() == "":
            err['pd_ver'] = "产品版本不能为空！"
        if shell_type.strip() == "":
            err['shell_type'] = "计划类型不能为空!"
        if shell_detail.strip() == "":
            err['shell_detail'] = "计划详情不能为空!"
        if len(err) > 0:
            return common_response(data=err, err=500, msg="参数错误，请查看接口返回!")
        try:
            d = {
                "_id": get_mongo_index('shells'),
                "name": name,
                "pd": product_id,
                "pd_ver": pd_ver,
                "type": shell_type,
                "detail": shell_detail,
                "author": current_user.username,
                "create_time": time.time(),
                "update_time": time.time()
            }
            data = pl.table.insert_one(d)
            return common_response(data={"_id": data.inserted_id}, err=0, msg="添加成功！")
        except Exception as e:
            app.logger.error(str(e))
            return common_response(data='', err=500, msg='添加失败')


@shell.route('/detail', methods=['GET'])
@login_required
def detail():
    r = request.args
    shell_id = r.get('shell_id', '')
    product_id = r.get('product_id', '')
    if shell_id.strip() == "":
        flash("shell_id 不能为空！")
        return redirect(request.referrer)
    pd = Product()
    pl = Shell()
    prod = pd.table.find_one({"_id": int(product_id)})
    data = pl.table.find_one({"_id": int(shell_id)})
    return render_template('shell/shell.detail.html', shell=data, product=prod)


@shell.route('/del', methods=['DELETE'])
@login_required
def delete():
    r = request.form
    pl = Shell()
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


@shell.route('/update', methods=['GET', 'PUT'])
@login_required
def update():
    pl = Shell()
    pv = ProductVersion()
    if request.method == "GET":
        r = request.args
        pd = Product()
        product_id = r.get('product_id', '')
        shell_id = r.get('shell_id', '')
        pd_ver = pv.table.find({"pd": product_id}, {"ver": 1}).sort([("_id", -1)]).limit(20)
        data = pl.table.find_one({"_id": int(shell_id)})
        prod = pd.table.find_one({"_id": int(product_id)})
        return render_template('shell/shell.edit.html', product=prod, versions=pd_ver, shell=data)

    if request.method == "PUT":
        r = request.form
        shell_id = r.get('shell_id', '')
        name = r.get('shell_name', '')
        product_id = r.get('product_id', '')
        pd_ver = r.get('pd_ver', '')
        shell_type = r.get('shell_type', '')
        shell_detail = r.get('shell_detail', '')
        err = {}
        if shell_id.strip() == "":
            err['shell_id'] = "shell_id 不能为空!"
        if name.strip() == "":
            err['name'] = "计划名称不能为空!"
        if product_id.strip() == "":
            err['product_id'] = "产品ID不能为空!"
        if pd_ver.strip() == "":
            err['pd_ver'] = "产品版本不能为空！"
        if shell_type.strip() == "":
            err['shell_type'] = "计划类型不能为空!"
        if shell_detail.strip() == "":
            err['shell_detail'] = "计划详情不能为空!"
        if len(err) > 0:
            return common_response(data=err, err=500, msg="参数错误，请查看接口返回!")
        try:
            q = {"_id": int(shell_id)}
            d = {
                "$set": {
                    "name": name,
                    "pd_ver": pd_ver,
                    "type": shell_type,
                    "detail": shell_detail,
                    "update_time": time.time()
                }
            }
            data = pl.table.update_one(q, d)
            return common_response(data={"result": data.raw_result}, err=0, msg="更新成功！！")
        except Exception as e:
            app.logger.error(str(e))
            return common_response(data='', err=500, msg='更新失败！')


@shell.route('/query', methods=['GET'])
def query():
    r = request.args
    pl = Shell()
    pd = r.get('pd', '').strip()
    ver = r.get('pd_ver', '').strip()
    try:
        data = pl.table.find({"pd": pd, "pd_ver": ver})
        data = list_mongo_res(data)
        return common_response(data=data, err=0, msg="请求成功！")
    except Exception as e:
        app.logger.error(str(e))
        return common_response(data='', err=500, msg="请求失败!")
