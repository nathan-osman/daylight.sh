/* The MIT License (MIT)
 *
 * Copyright (c) 2019 Nathan Osman
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

$(function() {

  // Time format for the times
  var TIME_FMT = "h:mma";

  // Grab references to the input fields
  var $timezone = $('input[name=timezone]');
  var $latitude = $('input[name=latitude]');
  var $longitude = $('input[name=longitude]');
  var $timezone = $('input[name=timezone]');
  var $year = $('input[name=year]');
  var $month = $('input[name=month]');
  var $day = $('input[name=day]');

  // Grab references to the spinner and result block
  var $spinner = $('#spinner');
  var $result = $('#result');

  // Initialize the date fields with the current date
  // (prefer the browser's values over the auto ones)
  if (!isPost) {
    var d = new Date();
    $timezone.val(moment.tz.guess().name);
    $year.val(d.getYear() + 1900);
    $month.val(d.getMonth() + 1);
    $day.val(d.getDate());
  }

  // Perform the calculation and update the result display
  function calculate() {
    $spinner.show();
    $result.hide();
    $.ajax({
      method: 'POST',
      url: "/",
      contentType: 'application/json',
      data: JSON.stringify({
        latitude: parseFloat($latitude.val()),
        longitude: parseFloat($longitude.val()),
        year: parseFloat($year.val()),
        month: parseFloat($month.val()),
        day: parseFloat($day.val()),
        timezone: $timezone.val()
      })
    })
    .done(function (d) {
      $('#sunrise .value').text(moment.unix(d.sunrise).format(TIME_FMT));
      $('#sunset .value').text(moment.unix(d.sunset).format(TIME_FMT));
      $result.show();
    })
    .always(function () {
      $spinner.hide();
    });
  }

  // Initialize the location fields if available
  // (prefer the browser's values over the auto ones)
  if (!isPost && navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(pos) {
      $latitude.val(pos.coords.latitude);
      $longitude.val(pos.coords.longitude);
      $timezone.val(moment.tz.guess());
      calculate();
    });
  }

  // Set the event handler for the form
  $('form').on('submit', function(e) {
    e.preventDefault();
    calculate();
  });

});
