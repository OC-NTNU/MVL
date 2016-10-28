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


// init elements

// NB creating a for-loop to init events 1 and 2 won't not work,
// because if the counter is inside a function body, its value will not be fixed
// until the body is executed!


// create query builder for event1 types
$('#builder-event-1').queryBuilder(event_options);

// create table for event1 types
$('#types-table-event-1').DataTable({
    select: {
        style: 'single'
    },
    columns: [
        {data: 'eventCount', title: 'Count', width: "10%"},
        {data: 'eventType', title: 'Predicate', width: "20%"},
        {data: 'variableType', title: 'Variable'}
    ]
}).on('select', function (e, dt, type, indexes) {
    var row = dt.row(indexes[0]).data();
    var pay_load = {
        event_direction: row.eventType,
        variable_string: row.variableType
    };
    $.ajax({
        url: $EVENT_INST_URL,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify(pay_load),
        complete: function (data, status) {
            showEventInstances(data, 1)
        }
    });
});

// search buttons for event1 types
$('#search-button-event-1').on('click', function () {
    searchEvent(1)
});

// reset button for event1 types & instances
$('#reset-button-event-1').on('click', function () {
    resetEvent(1);
})


// create query builder for event2 types
$('#builder-event-2').queryBuilder(event_options);

// create table for event2 types
$('#types-table-event-2').DataTable({
    select: {
        style: 'single'
    },
    columns: [
        {data: 'eventCount', title: 'Count', width: "10%"},
        {data: 'eventType', title: 'Predicate', width: "20%"},
        {data: 'variableType', title: 'Variable'}
    ]
}).on('select', function (e, dt, type, indexes) {
    var row = dt.row(indexes[0]).data();
    var pay_load = {
        'event': row.eventType,
        'var': row.variableType
    };
    $.ajax({
        url: $EVENT_INST_URL,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify(pay_load),
        complete: function (data, status) {
            showEventInstances(data, 2)
        }
    });
});

// search buttons for event2 types
$('#search-button-event-2').on('click', function () {
    searchEvent(2)
});

// reset button for event2 types & instances
$('#reset-button-event-2').on('click', function () {
    resetEvent(2);
})


function searchEvent(id) {
    $('#types-panel-event-' + id).addClass('hide');
    $('#instances-panel-event-' + id).addClass('hide');
    var pay_load = {
        rules: $('#builder-event-' + id).queryBuilder('getRules'),
        with_special: $('#checkbox-special-event-' + id).prop('checked'),
        with_general: $('#checkbox-general-event-' + id).prop('checked')
    }
    $.ajax({
        url: $EVENT_TYPE_URL,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify(pay_load),
        complete: function (data, status) {
            showEventTypes(data, id);
        }
    })
}


function showEventTypes(data, id) {
    $('#types-panel-event-' + id).removeClass('hide').scrollView();
    //console.log(data.responseJSON);
    var table = $('#types-table-event-' + id).DataTable()
        .clear()
        .rows.add(data.responseJSON)
        .columns.adjust()
        .draw();
}


function showEventInstances(data, id) {
    //console.log(data.responseText);
    $('#instances-panel-event-' + id).removeClass('hide').scrollView();
    var table = $('#instances-table-event-' + id).DataTable({
        destroy: true,
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

// create query builder for relations
$('#builder-relation').queryBuilder(relation_options);


// create table for relation types

$('#types-table-relation').DataTable({
    select: {
        style: 'single'
    },
    columns: [
        {data: 'relationCount', title: 'Count', width: "5%"},
        {data: 'relation', title: 'Relation', width: "10%"},
        {data: 'event1', title: 'Predicate1', width: "10%"},
        {data: 'variable1', title: 'Variable1'},
        {data: 'event2', title: 'Predicate2', width: "10%"},
        {data: 'variable2', title: 'Variable2'}
    ],
    rowId: 'relationId'
}).on('select', function (e, dt, type, indexes) {
    var row = dt.row(indexes[0]).data();
    var pay_load = {
        'event1': row.event1,
        'event2': row.event2,
        'variable1': row.variable1,
        'variable2': row.variable2,
        'relation': row.relation
    };
    //console.log(JSON.stringify(pay_load));
    $.ajax({
        url: $RELATION_INST_URL,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify(pay_load),
        complete: function (data, status) {
            showRelationInstances(data, status);
            var selectedEdge = parseInt(network.getSelectedEdges()[0]);
            //console.log(selectedEdge);
            //console.log(row.relationId)
            if (selectedEdge !== row.relationId) {
                //console.log("calling selectEdges");
                network.selectEdges([row.relationId]);
                network.focus(row.nodeId1)
            }
        }
    });
});

// create table for relation instances

$('#instances-table-relation').DataTable({
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

// search relation types

$('#search-button-relation').on('click', function () {
    $('#types-panel-relation').addClass('hide');
    $('#instances-panel-relation').addClass('hide');

    var pay_load = {
        event_1: {
            rules: $('#builder-event-1').queryBuilder('getRules'),
            with_special: $('#checkbox-special-event-1').prop('checked'),
            with_general: $('#checkbox-general-event-1').prop('checked')
        },
        event_2: {
            rules: $('#builder-event-2').queryBuilder('getRules'),
            with_special: $('#checkbox-special-event-1').prop('checked'),
            with_general: $('#checkbox-general-event-1').prop('checked')
        },
        relation: {
            rules: $('#builder-relation').queryBuilder('getRules')
        }
    };

    //console.log(rules);
    $.ajax({
        url: $RELATION_TYPE_URL,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        data: JSON.stringify(pay_load),
        complete: function (data, status) {
            showRelationTypes(data);
            showGraph(data)
        }
    })
})


// show relations

function showRelationTypes(data) {
    $('#types-panel-relation').removeClass('hide').scrollView();
    $('#types-table-relation').DataTable()
        .clear()
        .rows.add(data.responseJSON)
        .columns.adjust()
        .draw();
}

function showRelationInstances(data) {
    $('#instances-panel-relation').removeClass('hide').scrollView();
    $('#instances-table-relation').DataTable()
        .clear()
        .rows.add(data.responseJSON)
        .columns.adjust()
        .draw();
}

// reset relations

$('#reset-button-relation').on('click', function () {
    $('#builder-relation').queryBuilder('reset');
    $('#types-panel-relation').addClass('hide');
    $('#instances-panel-relation').addClass('hide');
    $('#graph-panel').addClass('hide');
})

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
    interaction: {
        // TODO these options have no effect
        hoverConnectedEdges: true,
        selectConnectedEdges: false
    },
    physics: {
        /* "repulsion": {
         "nodeDistance": 100
         }, */
        minVelocity: 0.75,
        solver: "repulsion"
    },
    // FIXME: find nav images (see vis/dist/img/network/)
    interaction: {
        navigationButtons: true,
        keyboard: true
    }

};


function showGraph(data) {
    $('#graph-panel').removeClass('hide');

    var records = data.responseJSON;
    var nodes = new vis.DataSet();
    var edges = new vis.DataSet();

    records.forEach(function (record) {
        // add first node
        try {
            nodes.add({
                id: record.nodeId1,
                label: wordWrap(record.variable1),
                title: 'n=' + record.eventCount1,
                group: record.event1,
                value: record.eventCount1
            })
        }
        catch (ex) { // node exists already
        }

        // add second node
        try {
            nodes.add({
                id: record.nodeId2,
                label: wordWrap(record.variable2),
                title: 'n=' + record.eventCount2,
                group: record.event2,
                value: record.eventCount2
            })
        }
        catch (ex) { // node exists already
        }

        var head = (record.relation == 'CAUSES');

        // add edge
        try {
            edges.add({
                id: record.relationId,
                from: record.nodeId1,
                to: record.nodeId2,
                value: record.relationCount,
                title: 'n=' + record.relationCount,
                //label: record.relationId
                arrows: {to: head}
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
        //console.log("on selectEdge");
        //console.log(params);
        // select corresponding row in table with relation types
        var rowId = '#' + params.edges[0];
        $('#types-table-relation').DataTable().row(rowId).draw().show().draw(false).select()
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
