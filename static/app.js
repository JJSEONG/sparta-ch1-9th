/** get_items()
 *  @Param store   - 편의점 목록 ("gs", "cu", "s11", "e24")
 *  @Param sortKey - 정렬 방식 (최신순: "_id", 리뷰 수: "review", 좋아요 수: "like")
 *  @Param lastId  - 스크롤 방식을 위한 가장 마지막 id를 반환
 *  @Param search  - 검색어
 */
function get_items(store, sortKey, lastId, search) {
    $.ajax({
        type: 'GET',
        url: '/items',
        data: {
            'store': store,
            'sort_key': sortKey,
            'last_id': lastId,
            'search': search
        },
        success: function (response) {
            let rows = JSON.parse(response['items'])
            let count = JSON.parse(response['count'])
            for (const row of rows) {
                let id = row['_id']
                let title = row['title']
                let price = row['price']
                let image = row['image']
                let like = row['like']

                temp_html = `
                        <div class="item" onclick="location.href='item/${id}'">
                            <img src="${image}" alt="">
                            <div class="item-info">
                                <p>${title}</p>
                                <p>가격 : ${price} 원</p>
                            </div>
                            <div class="like-btn">
                                <p>♡ (${like})</p>
                            </div>
                        </div>
                        `
                $('.items').append(temp_html)
            }
        }
    })
}

function search_item() {
    let storeTags = $('#stores').children();
    let sortTags = $('#sort').children();
    for (const storeTag of storeTags) {
        storeTag.classList.remove('pick')
    }
    for (const sortTag of sortTags) {
        sortTag.classList.remove('pick')
    }

    let search = $("#name_search").val()
    $('.items').empty()
    get_items("", "_id", '3d109c700000000000000000', search)
}

function change_sort(sort) {
    let sortTags = $('#sort').children();
    for (const sortTag of sortTags) {
        sortTag.classList.remove('pick')
    }

    $(`#${sort}`).addClass("pick");
    let stores = $('#stores').children();
    let storeName = "";
    for (const store of stores) {
        if (store.className === "pick") {
            storeName = store.id
            break;
        }
    }
    $('.items').empty()
    get_items(storeName, sort, '3d109c700000000000000000', '')
}

function change_store(store) {
    let storeTags = $('#stores').children();
    for (const sortTag of storeTags) {
        sortTag.classList.remove('pick')
    }

    $(`#${store}`).addClass("pick");
    $('.items').empty()
    get_items(store, "_id", '3d109c700000000000000000', '')
}