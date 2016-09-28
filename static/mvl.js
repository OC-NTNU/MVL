/***********************************************************************
 * Events
 ***********************************************************************/


// query-builder options for events

var event_options = {
    filters: [
        {
            id: 'variable',
            type: 'string',
            size: 60,
            operators: [
                'equal', 'not_equal',
                'begins_with_word', 'not_begins_with_word',
                'contains_word', 'not_contains_word',
                'ends_with_word', 'not_ends_with_word',
                'begins_with_string', 'not_begins_with_string',
                'contains_string', 'not_contains_string',
                'ends_with_string', 'not_ends_with_string'
            ],
            description: 'restrict the value of variables'
            //default_value: 'iron'
        },
        {
            id: 'event',
            input: 'select',
            placeholder: 'Select an event type',
            values: {
                'Change': 'Change',
                'Increase': 'Increase',
                'Decrease': 'Decrease'
            },
            operators: ['equal', 'not_equal'],
            description: 'restrict the value of events'
        }
    ],
    default_filter: 'variable',
    display_empty_filter: false,
    allow_empty: true,
    plugins: {
        //'bt-tooltip-errors': {delay: 100},
        //'sortable': null,
        'filter-description': {mode: 'bootbox'}
        //'bt-selectpicker': null,
        //'unique-filter': null,
        //'bt-checkbox': {color: 'primary'},
        //'invert': null
    },
    operators: [
        {type: 'equal'},
        {type: 'not_equal'},

        {
            type: 'begins_with_word',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'words'
        },
        {
            type: 'not_begins_with_word',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'words'
        },

        {
            type: 'contains_word',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'words'
        },
        {
            type: 'not_contains_word',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'words'
        },

        {
            type: 'ends_with_word',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'words'
        },
        {
            type: 'not_ends_with_word',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'words'
        },

        {
            type: 'begins_with_string',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'strings'
        },
        {
            type: 'not_begins_with_string',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'strings'
        },

        {
            type: 'contains_string',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'strings'
        },
        {
            type: 'not_contains_string',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'strings'
        },

        {
            type: 'ends_with_string',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'strings'
        },
        {
            type: 'not_ends_with_string',
            nb_inputs: 1,
            apply_to: ['string'],
            optgroup: 'strings'
        }
    ],
    lang: {
        operators: {
            equal: 'is',
            not_equal: 'is not',

            begins_with_word: 'begins with word',
            not_begins_with_word: 'does not begin with word',

            contains_word: 'contains word',
            not_contains_word: 'does not contain word',

            ends_with_word: 'ends with word',
            not_ends_with_word: 'does not end with word',

            begins_with_string: 'begins with string',
            not_begins_with_string: 'does not begin with string',

            contains_string: 'contains string',
            not_contains_string: 'does not contain string',

            ends_with_string: 'ends with string',
            not_ends_with_string: 'does not end with string'
        }
    }
};

// init

$('#builder-event-1').queryBuilder(event_options);
$('#builder-event-2').queryBuilder(event_options);


// search event types

$('#search-button-event-1').on('click', function () {
    searchEvent(1)
});

$('#search-button-event-2').on('click', function () {
    searchEvent(2)
});

function searchEvent(id) {
    $('#types-panel-event-' + id).addClass('hide');
    $('#instances-panel-event-' + id).addClass('hide');
    var rules = $('#builder-event-' + id).queryBuilder('getRules');
    //console.log(rules);
    $.ajax({
        url: $EVENT_TYPE_URL,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify(rules),
        complete: function (data, status) {
            showEventTypes(data, id);
        }
    })
}


// show events

function showEventTypes(data, id) {
    $('#types-panel-event-' + id).removeClass('hide').scrollView();
    var table = $('#types-table-event-' + id).DataTable({
        destroy: true,
        select: {
            style: 'single'
        },
        order: [],
        data: data.responseJSON,
        columns: [
            {data: 'eventCount', title: 'Count', width: "10%"},
            {data: 'event', title: 'Predicate', width: "20%"},
            {data: 'variable', title: 'Variable'} //,
            //{data: 'nodeId', title: 'Id'}
        ]
    });

    table
        .on('select', function (e, dt, type, indexes) {
            // TODO: pass only single node id
            var row = table.row(indexes[0]).data();
            var pay_load = {node_ids: [row.nodeId]};
            $.ajax({
                url: $EVENT_INST_URL,
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                data: JSON.stringify(pay_load),
                complete: function (data, status) {
                    showEventInstances(data, id)
                }
            });
        });
}


function showEventInstances(data, id) {
    //console.log(data.responseText);
    $('#instances-panel-event-' + id).removeClass('hide').scrollView();
    var table = $('#instances-table-event-' + id).DataTable({
        destroy: true,
        order: [],
        data: data.responseJSON.data,
        columns: [
            {title: 'Sentence'},
            {title: 'Year', width: "10%"},
            {title: 'Source', width: "10%", orderable: false}
        ],
        // FIXME: this is legacy, but drawCallback is not called
        fnDrawCallback: function (oSettings) {
            $("[data-toggle=popover]").popover(
                {
                    html: true,
                    container: 'body'
                });
        },
        drawCallback: function (settings) {
            console.log("DrawCallback")
        }
    })
}


// reset events

$('#reset-button-event-1').on('click', function () {
    resetEvent(1);
});

$('#reset-button-event-2').on('click', function () {
    resetEvent(2);
});

function resetEvent(id) {
    $('#builder-event-' + id).queryBuilder('reset');
    $('#types-panel-event-' + id).addClass('hide');
    $('#instances-panel-event-' + id).addClass('hide');
}


/***********************************************************************
 * Relations
 ***********************************************************************/

// query-builder options for relations

var relation_options = {
    filters: [
        {
            id: 'cooccurs',
            type: 'string',
            size: 60,
            operators: [
                'greater', 'equal', 'less'
            ],
            default_value: 0,
            min: 0,
            description: 'search for co-occurring venets'
        },
        {
            id: 'causes',
            type: 'string',
            size: 60,
            operators: [
                'greater', 'equal', 'less'
            ],
            default_value: 0,
            min: 0,
            description: 'search for causally related events'
        }
    ],
    allow_empty: true,
    default_filter: 'cooccurs',
    display_empty_filter: false,
    plugins: {
        //'bt-tooltip-errors': {delay: 100},
        //'sortable': null,
        'filter-description': {mode: 'bootbox'}
        //'bt-selectpicker': null,
        //'unique-filter': null,
        //'bt-checkbox': {color: 'primary'},
        //'invert': null
    }
};

// init

$('#builder-relation-1').queryBuilder(relation_options);

// search relation types

$('#search-button-relation-1').on('click', function () {
    searchRelation("1")
});

function searchRelation(id) {
    $('#types-panel-relation-' + id).addClass('hide');
    $('#instances-panel-relation-' + id).addClass('hide');

    var rules = {
        'event_1': $('#builder-event-1').queryBuilder('getRules'),
        'event_2': $('#builder-event-2').queryBuilder('getRules'),
        'relation': $('#builder-relation-' + id).queryBuilder('getRules')
    };

    //console.log(rules);
    $.ajax({
        url: $RELATION_TYPE_URL,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify(rules),
        complete: function (data, status) {
            showRelationTypes(data, id);
            showGraph(data, id)
        }
    })
}


// show relations

function showRelationTypes(data, id) {
    $('#types-panel-relation-' + id).removeClass('hide').scrollView();
    var table = $('#types-table-relation-' + id).DataTable({
        destroy: true,
        order: [],
        select: {
            style: 'single'
        },
        data: data.responseJSON,
        columns: [
            {data: 'relationCount', title: 'Count', width: "5%"},
            {data: 'relation', title: 'Relation', width: "10%"},
            {data: 'event1', title: 'Predicate1', width: "10%"},
            {data: 'variable1', title: 'Variable1'},
            {data: 'event2', title: 'Predicate2', width: "10%"},
            {data: 'variable2', title: 'Variable2'},
            //{data: 'nodeId1', name: 'nodeId1', title: 'nodeId1'},
            //{data: 'nodeId2', name: 'nodeId2', title: 'nodeId2'},
            //{data: 'relationId', name: 'relId', title: 'relId'}
        ],
        rowId: 'relationId'
    });
    $('#types-panel-relation-' + id).scrollView();

    table.on('select', function (e, dt, type, indexes) {
        // For some reason, this does not work:
        //     var row =  table.row(indexes[0]).data();
        // so we do this instead:
        var t = $('#types-table-relation-' + id).DataTable();
        var row = t.row(indexes[0]).data();
        var pay_load = {rel_type_info: [row.nodeId1, row.relation, row.nodeId2]};
        //console.log(JSON.stringify(pay_load));
        $.ajax({
            url: $RELATION_INST_URL,
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            data: JSON.stringify(pay_load),
            complete: function (data, status) {
                showRelationInstances(data, status, id);
                network.selectEdges([row.relationId]);
                network.focus(row.nodeId1)
            }
        });
    });
}


function showRelationInstances(data, status, id) {
    $('#instances-panel-relation-' + id).removeClass('hide').scrollView();
    var table = $('#instances-table-relation-' + id).DataTable({
        destroy: true,
        order: [],
        data: data.responseJSON,
        columns: [
            {data: 'sentence', title: 'Sentence'},
            {data: 'year', title: 'Year', width: "10%"},
            {data: 'source', title: 'Source', width: "10%", orderable: false}
        ],
        // FIXME: this is legacy, but drawCallback is not called
        fnDrawCallback: function (oSettings) {
            $("[data-toggle=popover]").popover(
                {
                    html: true,
                    container: 'body'
                });
        },
    });

    // TODO: get popover/tooltip to work
    // table.on( 'draw.dt', function () {
    //   table.$("a[rel=popover]").popover().click(function(e) {e.preventDefault();});
    // } );
}

// reset relations

$('#reset-button-relation-1').on('click', function () {
    resetRelation(1)
});

function resetRelation(id) {
    $('#builder-relation-' + id).queryBuilder('reset');
    $('#types-panel-relation-' + id).addClass('hide');
    $('#instances-panel-relation-' + id).addClass('hide');
    $('#graph-panel-' + id).addClass('hide');
}

/***********************************************************************
 * Graph
 ***********************************************************************/

// TODO: remove global var network?
var network;


var graph_options = {
    groups: {
        Change: {
            shape: 'diamond',
            color: {
                background: '#5cb85c'
            }
        },
        Increase: {
            shape: 'triangle',
            color: {
                background: '#d9534f'
            }
        },
        Decrease: {
            shape: 'triangleDown',
            color: {
                background: '#337ab7'
            }
        }
    },
    edges: {
        color: {
            color: 'grey',
            highlight: 'black'
        },
        shadow: true
    },
    nodes: {
        size: 10,
        shadow: true,
        color: {
            border: 'black'
        },
        scaling: {
            label: {
                maxVisible: 14
            }
        }
    },
    "physics": {
        /* "repulsion": {
         "nodeDistance": 100
         }, */
        "minVelocity": 0.75,
        "solver": "repulsion"
    },
    // FIXME: find nav images (see vis/dist/img/network/)
    interaction: {
        navigationButtons: true,
        keyboard: true
    }

};


function showGraph(data, id) {
    $('#graph-panel-' + id).removeClass('hide');

    var records = data.responseJSON;
    var nodes = new vis.DataSet();
    var edges = new vis.DataSet();

    records.forEach(function (record) {
        // add first node
        try {
            nodes.add({
                id: record.nodeId1,
                label: wordWrap(record.variable1),
                group: record.event1
            })
        }
        catch (ex) { // node exists already
        }

        // add first node
        try {
            nodes.add({
                id: record.nodeId2,
                label: wordWrap(record.variable2),
                group: record.event2
            })
        }
        catch (ex) { // node exists already
        }

        // add edge
        try {
            edges.add({
                id: record.relationId,
                from: record.nodeId1,
                to: record.nodeId2,
                value: record.relationCount,
                title: record.relation,
                //label: record.relationId
            })
        }
        catch (ex) { // edge already exists - should not happen?
        }
    });

    var container = document.getElementById('event-graph');

    var graphData = {
        nodes: nodes,
        edges: edges
    };

    // TODO: update graph instead of creating new instance?
    network = new vis.Network(container, graphData, graph_options);

    network.on("selectEdge", function (params) {
        // select corresponding row in table with relation types
        var rowId = '#' + params.edges[0];
        $('#types-table-relation-' + id).DataTable().row(rowId).draw().show().draw(false).select()
    })
}


// utility functions

function wordWrap(text, width) {
    width = width || 32;
    var re = new RegExp("([\\w\\s]{" + (width - 2) + ",}?\\w)\\s?\\b", "g");
    return text.replace(re, "$1\n")
}

/**
 *   Scroll table to show a certain row
 *
 *   Source: https://datatables.net/plug-ins/api/row().show()
 */
$.fn.dataTable.Api.register('row().show()', function () {
    var page_info = this.table().page.info();
    // Get row index
    var new_row_index = this.index();
    // Row position
    var row_position = this.table().rows()[0].indexOf(new_row_index);
    // Already on right page ?
    if (row_position >= page_info.start && row_position < page_info.end) {
        // Return row object
        return this;
    }
    // Find page number
    var page_to_display = Math.floor(row_position / this.table().page.len());
    // Go to that page
    this.table().page(page_to_display);
    // Return row object
    return this;
});

$.fn.scrollView = function () {
    return this.each(function () {
        $('html, body').animate({
            scrollTop: $(this).offset().top - 60
        }, 1000);
    });
}


/***********************************************************************
 * Development
 ***********************************************************************/

/*

$('#builder-event-2').queryBuilder('setRules', {
    'rules': [{
        'value': 'Decrease',
        'field': 'event',
        'operator': 'equal',
        'input': 'select',
        'type': 'string',
        'id': 'event'
    }],
    'condition': 'AND'
});

$('#builder-event-1').queryBuilder('setRules', {
    'rules': [{
        'value': 'Increase',
        'field': 'event',
        'operator': 'equal',
        'input': 'select',
        'type': 'string',
        'id': 'event'
    }],
    'condition': 'AND'
});

$('#builder-relation-1').queryBuilder('setRules', {
    'rules': [{
        'value': '1',
        'field': 'cooccurrence',
        'operator': 'greater',
        'input': 'text',
        'type': 'string',
        'id': 'cooccurrence'
    }],
    'condition': 'AND'
});

*/

$(document).ready(function () {
    $('[data-toggle="popover"]').popover();
});
