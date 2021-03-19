let all_segments_with_id = function (id) {
    return $("polyline[id=" + id + "]");
};

let get_id = function(item) {
    return item.attr('id');
};

$(document).ready(function () {
    let object_segments = $('.object-segment');
    let is_empty = $('#is-empty');
    let submit_button = $('#submit-button');
    let submit_button_save = $('#submit-button-save');
    let show_all = $('#show-all');

    let update_state = function() {
        // update color of the segments
        object_segments.removeClass('object-segment-selected');
        for (let po of preferred_objects) {
            all_segments_with_id(po.toString()).addClass('object-segment-selected');
        }

        // update buttons
        if (preferred_objects.size > 0) {
            submit_button.removeClass('btn-secondary');
            submit_button.addClass('btn-primary');
            submit_button.prop('disabled', false);

            submit_button_save.removeClass('btn-outline-secondary');
            submit_button_save.addClass('btn-outline-primary');
            submit_button_save.prop('disabled', false);

            is_empty.prop('checked', false).prop('disabled', true);
        } else {
            is_empty.prop('disabled', false);
            if (document.getElementById('is-empty').checked) {
                submit_button.removeClass('btn-secondary');
                submit_button.addClass('btn-primary');
                submit_button.prop('disabled', false);

                submit_button_save.removeClass('btn-outline-secondary');
                submit_button_save.addClass('btn-outline-primary');
                submit_button_save.prop('disabled', false);
            } else {
                submit_button.addClass('btn-secondary');
                submit_button.removeClass('btn-primary');
                submit_button.prop('disabled', true);

                submit_button_save.addClass('btn-outline-secondary');
                submit_button_save.removeClass('btn-outline-primary');
                submit_button_save.prop('disabled', true);
            }
        }
    };

    object_segments.mouseover(function () {
        // we need all the elements with such id.
        all_segments_with_id(get_id($(this))).addClass('object-segment-active');
    });
    object_segments.mouseleave(function () {
        all_segments_with_id(get_id($(this))).removeClass('object-segment-active');
    });

    object_segments.click(function () {
        let current_id = parseInt(get_id($(this)));
        if (preferred_objects.has(current_id)) {
            preferred_objects.delete(current_id);
        } else {
            preferred_objects.add(current_id);
        }
        update_state();
    });

    is_empty.change(function () {
        update_state();
    });

    submit_button.click(function () {
        $('#preferred-objects-input').val(Array.from(preferred_objects).join(","));
    });

    submit_button_save.click(function () {
        $('#preferred-objects-input').val(Array.from(preferred_objects).join(","));
    });

    show_all.mouseover(function () {
        object_segments.addClass('force-show');
    });
    show_all.mouseleave(function () {
        object_segments.removeClass('force-show');
    });

    update_state();
});