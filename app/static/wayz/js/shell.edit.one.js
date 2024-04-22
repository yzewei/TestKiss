//两个编辑框实现粘贴图片功能
$(function () {
    document.getElementById('editor-one').addEventListener('paste',function(e){
    if ( !(e.clipboardData && e.clipboardData.items) ) {
        return;
    }
    for (let i = 0, len = e.clipboardData.items.length; i < len; i++) {
        let item = e.clipboardData.items[i];

        if (item.kind === "string") {
            item.getAsString(function (str) {
                console.log(str);
            })
        } else if (item.type === "image/png") {
            let f= item.getAsFile();
            console.log(f.height);
            console.log(f.width);
            let reader=new FileReader();
            reader.readAsDataURL(f);
                    reader.onload=function(e){
                    let base64_str=this.result;
                    let img = new Image();

                    img.src = this.result.toString();
                    img.className = 'mg-responsive img-rounded';
                    img.style.maxWidth = '200px';
                    img.style.maxHeight = '180px';
                        $("#editor-one").append(img);
                    }
            console.log(item);
        }
    }
});
})

function update_shell() {
$("#update_shell").click(function () {
    let url = current_host + '/shell/update'
    let shell_id = $("#shell_id").val();
    let product_id = $("#product_id").val();
    let name = $("#shell_name").val();
    let pd_ver = $("#pd_ver").val();
    let shell_type = $("#shell_type").val();
    let shell_detail = $("#editor-one").html();
    if($.trim(name) == ""){
        msg("error", "计划名称不能为空!");
        return;
    }
    if($.trim(pd_ver) == ""){
        msg("error", "请选择一个产品版本");
        return;
    }
    if($.trim(shell_type) == 0){
        msg("error", "请选择一个计划类型");
        return;
    }
    if($.trim(shell_detail) == ""){
        msg("error", "请填写测试计划详情");
        return;
    }
    let data ="shell_id="+shell_id
        +"&shell_name="+encodeURIComponent(name)
        +"&product_id="+product_id
        +"&pd_ver="+pd_ver
        +"&shell_type="+shell_type
        +"&shell_detail="+encodeURIComponent(shell_detail)

    $.ajax({
    type :"PUT",
    url : url,
    dataType: "json",
    data : data,
    async : false,
    success : function(r){
        if(r.err == 0){
            console.log(r.data._id)
            msg("success", r.msg)
            window.location.href = $("#go_back").attr('href');
        }else{
            msg("error", r.msg);
        }
    },
    error: function(){
        msg("error", "服务端请求出错!");
    }
});
});
}

$(document).ready(function() {
update_shell();
});
